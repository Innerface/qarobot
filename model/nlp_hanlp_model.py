from jpype import *

startJVM(getDefaultJVMPath())
java.lang.System.out.println("hello world")
shutdownJVM()
