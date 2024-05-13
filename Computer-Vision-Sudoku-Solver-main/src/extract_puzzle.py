from tensorflow import keras
from keras.models import load_model
from imutils.perspective import four_point_transform
from skimage.segmentation import clear_border
import numpy as np
import imutils
import cv2 as cv
from src.test import solve


def find_puzzle(image, debug=False):
	"""
	Find the Sudoku puzzle grid in the input image and perform perspective transform.

	Parameters:
		image (Mat): The input image containing the Sudoku puzzle.
		debug (bool, optional): If True, shows intermediate steps using cv2.imshow.

	Returns:
		tuple: A tuple containing the original puzzle grid and the warped grid.
	"""
	gray = cv.cvtColor(src=image, code=cv.COLOR_BGR2GRAY)  # Convert to grayscale
	blurred = cv.GaussianBlur(src=gray, ksize=(0,0), sigmaX=3)  # Blendes noise away

	thresh = cv.adaptiveThreshold(src=blurred, maxValue=255, 
			       adaptiveMethod=cv.ADAPTIVE_THRESH_GAUSSIAN_C, 
				   thresholdType=cv.THRESH_BINARY, blockSize=13, C=2)
	thresh = cv.bitwise_not(src=thresh)  # Contours become white

	contours = cv.findContours(image=thresh.copy(), mode=cv.RETR_EXTERNAL, method=cv.CHAIN_APPROX_SIMPLE)
	contours = imutils.grab_contours(cnts=contours)

	puzzle_contour = None
	for contour in sorted(contours, key=cv.contourArea, reverse=True):
		perimeter = cv.arcLength(curve=contour, closed=True)
		estimate = cv.approxPolyDP(curve=contour, epsilon=0.02*perimeter, closed=True)

		if len(estimate) == 4:  # Largest contour with 4 corners most likely to be the border
			puzzle_contour = estimate
			break
	else:
		raise("Could not identify a puzzle")

	# Get bird view of the puzzle
	puzzle = four_point_transform(image=image, pts=puzzle_contour.reshape(4, 2))
	rectified_puzzle = four_point_transform(image=gray,  pts=puzzle_contour.reshape(4, 2))
	
	if debug:
		cv.imshow("Puzzle Input", image)
		cv.waitKey(0)

		cv.imshow("Puzzle Gray", gray)
		cv.waitKey(0)

		cv.imshow("Puzzle Blurred", blurred)
		cv.waitKey(0)

		cv.imshow("Puzzle Thresh", thresh)
		cv.waitKey(0)

		cv.drawContours(image=image, contours=[puzzle_contour], contourIdx=-1, color=(0, 0, 255), thickness=4)
		cv.imshow("Puzzle Outline", image)
		cv.waitKey(0)

		cv.imshow("Puzzle Transform", puzzle)
		cv.waitKey(0)

		cv.imshow("Rectified Puzzle ", rectified_puzzle)
		cv.waitKey(0)
	
	return (puzzle, rectified_puzzle)


def extract_digit(cell, debug=False):
	"""
	Extract a single digit from a cell of the Sudoku grid.

	Parameters:
		cell (numpy.ndarray): The cell image containing the digit.
		debug (bool, optional): If True, shows intermediate steps using cv2.imshow.

	Returns:
		numpy.ndarray or None: The extracted digit image or None if the cell is empty or noise.
	"""
	_, thresh = cv.threshold(src=cell, thresh=0, maxval=255, type= cv.THRESH_BINARY_INV | cv.THRESH_OTSU)
	thresh = clear_border(thresh)

	contours = cv.findContours(image=thresh, mode=cv.RETR_EXTERNAL, method=cv.CHAIN_APPROX_SIMPLE)
	contours = imutils.grab_contours(cnts=contours)

	# Empty cell
	if len(contours) == 0:
		return None

	# Get largest contour
	mask = np.zeros(thresh.shape, dtype="uint8")
	contour = max(contours, key=cv.contourArea)
	cv.drawContours(image=mask, contours=[contour], contourIdx=-1, color=255, thickness=-1)

	h, w = thresh.shape
	if cv.countNonZero(mask)/float(h*w) <= 0.05:  # Likely just noise --> 0
		return None

	digit = cv.bitwise_and(src1=thresh, src2=thresh, mask=mask)

	if debug:
		cv.imshow("Thresh", thresh)
		cv.waitKey(0)
		cv.imshow("Digit", digit)
		cv.waitKey(0)

	return digit


def extract(image):
	puzzleImage, rectified_grid = find_puzzle(image, debug=True)

	# Initialize the board and model for digit classification
	board = np.zeros((9, 9), dtype="int")
	model = load_model('models/digit_classifier.h5', compile=False)

	dy, dx = tuple(dim // 9 for dim in rectified_grid.shape)
	cells = []

	# Process each cell in the rectified grid
	for y in range(9):
		rowCells = []
		
		y_start, y_end = y * dy, (y + 1) * dy

		for x in range(9):
			x_start, x_end = x * dx, (x + 1) * dx

			cell = rectified_grid[y_start:y_end, x_start:x_end]
			rowCells.append((x_start, y_start, x_end, y_end))

			# Extract the digit from the cell
			digit = extract_digit(cell, debug=False)
			if digit is not None:
				# Prepare the digit for classification
				roi = cv.resize(digit, (28, 28))
				roi = roi.astype("float") / 255.0
				roi = np.expand_dims(roi, axis=0)

				# Classify the digit using the model
				predictions = model.predict(roi, verbose=0)
				estimate = predictions.argmax(axis=1)[0]

				# 6 is seen as 8 many times
				# Possibility: use different CNN with other kernels in this case
				if estimate == 8 and predictions[0][6] > 0.002:
					estimate = 6

				# Update the Sudoku board with the estimated digit
				board[y, x] = estimate
		
		cells.append(rowCells)

	# Solve the Sudoku puzzle
	solution = solve(board)[0]
	return (solution, board, cells, puzzleImage)


def visualize(image):
	"""
	Process the input image to solve the Sudoku puzzle and visualize the result.

	Parameters:
		image (numpy.ndarray): The input image containing the Sudoku puzzle.

	Returns:
		None
	"""
	solution, board, cells, puzzleImage = extract(image)
	
	# Annotate the solution on the original image
	for r, (cellRow, solutionRow) in enumerate(zip(cells, solution)):
		for c, (cell, digit) in enumerate(zip(cellRow, solutionRow)):
			if not board[r, c]:  # Empty cell
				x_start, y_start, x_end, y_end = cell
				cv.putText(img=puzzleImage, text=str(digit), 
	       				   org=(int((x_end-x_start)*0.28)+x_start, int((y_end-y_start)*0.82)+y_start), 
						   fontFace=cv.FONT_HERSHEY_COMPLEX, fontScale=1,
						   color=(0, 0, 255), thickness=2)

	# Display the annotated Sudoku result
	cv.imshow("Solved Sudoku", puzzleImage)
	cv.waitKey(0)


if __name__ == "__main__":
	from camera import take_picture
	image = take_picture()
	# cv.imshow("Image", image)
	image = cv.resize(image, (500,500))
	visualize(image=image)
