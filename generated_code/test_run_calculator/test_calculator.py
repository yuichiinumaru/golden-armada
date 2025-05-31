import calculator

result = calculator.add(5, 3)
print(result)
#This part would ideally use a tool to execute the script and check the output
#For this example, we will just print a success message if the result is 8
if result == 8:
    print("Test passed!")
else:
    print("Test failed!")