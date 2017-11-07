import unittest
import fritzassignment

class TestAssignment(unittest.TestCase):

	#ßdef test_initialise(self):
		#fritzassignment.initialise()

	# def test_terminate(self):
	# 	fritzassignment.terminate()


	# def test_listItemsInBucket(self):
	#  	fritzassignment.listItemsInBucket()


	# def test_addToBucket(self):
	# 	fritzassignment.addToBucket()

	def test_menu(self):
		fritzassignment.menu()

if __name__ == '__main__':
	unittest.main()