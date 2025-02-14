# Author: Jason Kim
# Collaborators: Zachary Schmidt, Moaz Abdelmonem
# Oversight: Dr. David Nobes
# University of Alberta, Summer 2022, Curriculum Development Co-op Term

# This file contains all the functions needed to generate the JS of the 
# webpage which is not releated to the generation of the lines

# Dependencies: cleaner

from .. import cleaner

# Function that generates the JS before the generation of the course diagram.
# Mostly global variables and rendering functions
# Parameters:
#   controller - file handle for controller JS file
#   sequenceDict - dict that maps plan name to a dict that represents the plan sequence
def initializeControllerJavaScript(sequenceDict, initialCourseGroupVals, courseGroupDict, courseGroupList, controller):
    generateInitialBlockController(courseGroupDict, courseGroupList, controller)
    generatePlanBasedBlocksController(sequenceDict, 
                                      initialCourseGroupVals,
                                      courseGroupDict, 
                                      courseGroupList,
                                      controller)

# Function that generates the initial block of Javascript in controller.js
# Parameters:
#   controller - file handle for controller JS file
def generateInitialBlockController(courseGroupDict, courseGroupList, controller):
    planList = list(courseGroupDict.keys())
    controller.write("var app = angular.module(\"main\", []);\n")
    controller.write("app.controller(\"main\", function($scope) { \n")
    controller.write("$scope.selectedPlan = \"" + cleaner.cleanString(planList[0])+ "\";\n")  # var storing current plan name
    controller.write("var that = this;\n")

    # Render function, called when switching b/w plans
    controller.write("""this.render = function(plan) {
            this.disable(this.previousPlan);
            this.enable(plan);
            this.previousPlan = plan;
};\n""")

    controller.write("""var radios = document.querySelectorAll("input[type=radio][name=planselector]");
Array.prototype.forEach.call(radios, function (radio) {
    radio.addEventListener("change", function () { \n""")
    controller.write("that.setDefaults($scope.selectedPlan);\n")  # sets default plan, term, course group selections
    planString = generatePlanString(courseGroupList)
    controller.write("that.render("+planString+");\n")
    controller.write("""   });
});\n""")
    generateHighlightElement(controller)
    generateUnHighlightElement(controller)

# Function that writes the highlightElement function which highlights
# an individual course when a category button is pressed.
# Parameters:
#   controller - file handle to controller.js
def generateHighlightElement(controller):
    # check if element is highlighted already, if it isn't, add
    # "-highlighetd" to the end of the class name
    controller.write("""this.highlightElement = function(element, category) {
        if (element.classList.contains(category + "-highlighted")) {
            return;
        }
        element.classList.remove(category);
        element.classList.add(category + "-highlighted");
    };\n""")

# Function that writes the unhighlightElement function which unhighlights
# an individual course when a category button is pressed.
# Parameters:
#   controller - file handle to controller.js
def generateUnHighlightElement(controller):
    # if an element is in the highlighted state, remove "-highlighted"
    # from the class name
    controller.write("""this.unHighlightElement = function(element, category) {
        if (!element.classList.contains(category + "-highlighted")) {
            return;
        }
        element.classList.remove(category + "-highlighted");
        element.classList.add(category);
    };\n""")

# Function that generates the blocks of the controller JS file that are dependent
# on the number and names of plans provided
# Parameters:
#   sequenceDict - dict that maps plan name to a dict that represents the plan sequence
#   controller - file handle for controller.js file
def generatePlanBasedBlocksController(sequenceDict, initialCourseGroupVals, courseGroupDict, courseGroupList, controller):
    generatePlanBasedInitalVariables(sequenceDict, initialCourseGroupVals, courseGroupList, controller)
    generateSetDefaults(courseGroupDict, courseGroupList, controller)
    generateSubRadioListener(courseGroupList, controller)
    generateDisableSwitchStatement(sequenceDict, controller)
    generateEnableSwitchStatement(sequenceDict, controller)
    generateAddLineSwitch(sequenceDict, courseGroupList, controller)
    generateDeleteLineSwitch(sequenceDict, courseGroupList, controller)
    generateAddToClickSwitch(sequenceDict, courseGroupList, controller)
    generateDeleteFromClickSwitch(sequenceDict, courseGroupList, controller)
    generateCategoryLegendJS(sequenceDict, courseGroupList, controller)

# Function that generates the intial variables for the controller
# based on the plans
# Parameters: 
#   sequenceDict - dict that maps plan name to a dict that represents the plan sequence
#   controller - file handle for controller.js file
def generatePlanBasedInitalVariables(sequenceDict, initialCourseGroupVals, courseGroupList, controller):
    for plan in sequenceDict:
        controller.write("this." + cleaner.cleanString(plan) + "List = [];\n")  # list of lines displaying on plan
        controller.write("this." + cleaner.cleanString(plan) + "Clicked = [];\n")
        controller.write("this." + cleaner.cleanString(plan) + "LegendBtns = [];\n")
        controller.write("this." + cleaner.cleanString(plan) + "LegendBtnsClicked = [];\n")
        controller.write("this." + cleaner.cleanString(plan) + "ClickedMap = new Map();\n")
        numterms = len(sequenceDict[plan].keys())
        controller.write("this." + cleaner.cleanString(plan) + "Terms = " + str(numterms) + ";\n")
        maxcourses = 0
        for term in sequenceDict[plan]:
            termcourses = len(sequenceDict[plan][term])
            if termcourses > maxcourses:
                maxcourses = termcourses
        controller.write("this." + cleaner.cleanString(plan) + "MaxCourses = " + str(maxcourses) + ";\n")  # allows variable page height depending on number of courses
    for courseGroup in initialCourseGroupVals:
        formattedCourseGroupVar = "$scope.field{number} = {{ group{number}: \"{val}\" }};\n"
        controller.write(formattedCourseGroupVar.format(number=courseGroup, 
                                                        val=initialCourseGroupVals[courseGroup]))
    planString = generatePlanString(courseGroupList)
    controller.write("this.previousPlan = " + planString + "\n")

# Function that writes the setDefaults function based on the plans and course groups
# Parameters:
#   courseGroupDict - dict that maps plans to a dict that maps course groups to the 
#   options avaiable in that course group
#   courseGroupList - list of course groups taken overall in the program
#   controller - file handle to controller.js
def generateSetDefaults(courseGroupDict, courseGroupList, controller):
    controller.write("this.setDefaults = function(plan) { \n")
    controller.write("  switch(plan) { \n")
    formattedCaseStatement = "      case \"{case}\": \n"
    formattedCourseGroup = "            $scope.field{number}.group{number} ="
    switchEndString = """    default:
    console.log("shouldn't be here");
    }
};\n"""
    for mainPlan in courseGroupDict:
        controller.write(formattedCaseStatement.format(case=cleaner.cleanString(mainPlan)))
        for element in courseGroupList:
            controller.write(formattedCourseGroup.format(number=element))
            if element not in courseGroupDict[mainPlan]:
                controller.write("\"\";\n")
            else:
                controller.write("\""+str(element)+"A\";\n")
        controller.write("          $scope.$apply();\n")
        controller.write("          break;\n")
    controller.write(switchEndString)

# Function that generates the listener that listens to course group radio inputs
# Parameters:
#   courseGroupList - list of course groups taken in this program
#   controller - file handle to controller.js          
def generateSubRadioListener(courseGroupList, controller):
    planString = generatePlanString(courseGroupList)  # name of plan with course group on end (eg: "TraditionalPlan2A3A4B")
    controller.write("$scope.globalSubGroupChange = function () { \n")
    controller.write("that.render(" + planString + ");\n")  # update the page
    controller.write("};\n")

# Function that generates the switch statements and functions which handle
# disabling the lines of a plan when switched off
# Parameters:
#   sequenceDict - dict that maps plan name to a dict that represents the plan sequence
#   controller - file handle for controller.js file
def generateDisableSwitchStatement(sequenceDict, controller):
    formattedFunctionStatement = """this.{functionName} = function(plan) {{
    switch (plan) {{ \n"""
    formattedSwitchStatement = """  case "{planName}": 
    for (let i = 0; i < this.{planName}List.length; i++) {{
        this.{planName}List[i][0].{actionName}(true);
    }}
    break; \n"""
    switchEndString = """    default:
    console.log("shouldn't be here");
    }
};\n"""
    controller.write(formattedFunctionStatement.format(functionName="disable"))
    for plan in sequenceDict:
        controller.write(formattedSwitchStatement.format(planName=cleaner.cleanString(plan), 
                                                         actionName="hide"))
    controller.write(switchEndString)

# Function that generates the switch statements and functions which handle
# enabling of course boxes, lines between plans, and boxes that were highlighted
# from the legend.
# Parameters:
#   sequenceDict - dict that maps plan name to a dict that represents the plan sequence
#   controller - file handle for controller.js file
def generateEnableSwitchStatement(sequenceDict, controller):
    categoriesDict = sortIntoCategories(sequenceDict)  # sort courses into categories
    findLegendButtons(categoriesDict, sequenceDict, controller)  # find legend buttons in the document, store them in a list

    formattedFunctionStatement = """this.{functionName} = function(plan) {{
  switch(plan) {{\n"""

    # layout: for each plan, show/display every course box in that plan,
    # then adjust the webpage width and height, then (for loop #1) restore all courses
    # that were clicked to their clicked state (highlighted with arrows drawn).
    # For loop #2: Restore all courses that were highlighted with the legend buttons
    # to their highlighted state and restore legend buttons to their pressed state.
    formattedSwitchStatement = """    case "{planName}": 
      for (let i = 0; i < this.{planName}List.length; i++) {{
          this.{planName}List[i][0].{actionName}(true);
      }}
      width = this.{planName}Terms*220 + 20;
      widthstr = width.toString() + "px";
      document.getElementById("main").style.width = widthstr;
      height = this.{planName}MaxCourses*100 + 690;
      heightstr = height.toString() + "px";
      document.getElementById("main").style.height = heightstr;
      for (let i = 0; i < this.{planName}Clicked.length; i++) {{
          var element = document.getElementById(this.{planName}Clicked[i][0]);
          this.highlightElement(element, this.{planName}Clicked[i][1]);
      }}
      for (let i = 0; i < this.{planName}LegendBtns.length; i++) {{
          var found = false;
          for (let j = 0; j < this.{planName}LegendBtnsClicked.length; j++) {{
              if (this.{planName}LegendBtnsClicked[j] == this.{planName}LegendBtns[i]) {{
                  found = true;
              }}
          }}
          if (found == false) {{
            if (this.{planName}LegendBtns[i].classList.contains("legendbutton-pressed")) {{
              this.{planName}LegendBtns[i].classList.remove("legendbutton-pressed");
            }}
              this.{planName}LegendBtns[i].classList.add("legendbutton");
          }}
          if (found == true) {{
            if (this.{planName}LegendBtns[i].classList.contains("legendbutton")) {{
              this.{planName}LegendBtns[i].classList.remove("legendbutton");
            }}
              this.{planName}LegendBtns[i].classList.add("legendbutton-pressed");
          }}
      }}
      break; \n"""

    switchEndString = """    default:
    console.log("shouldn't be here");
    }
};\n"""

    controller.write(formattedFunctionStatement.format(functionName="enable"))
    for plan in sequenceDict:
        controller.write(formattedSwitchStatement.format(planName=cleaner.cleanString(plan), 
                                                         actionName="show"))
    controller.write(switchEndString)

# Function that generates the switch statement and function addLine
# Parameters:
#   sequenceDict - dict that maps plan name to a dict that represents the plan sequence
#   controller - file handle for controller.js file
def generateAddLineSwitch(sequenceDict, courseGroupList, controller):
    switchEndString = """    default:
    console.log("shouldn't be here");
    }
};\n"""
    formattedFunctionStatement = """this.{functionName} = function(line) {{
switch({planString}) {{ \n"""
    formattedAddLineSwitchStatement = """ case "{planName}":
    var index = this.{planName}List.findIndex((element) => element[0] == line);
    if (index == -1) {{
        line.show(false);
        this.{planName}List.push([line, 1])
    }}
    else {{
        this.{planName}List[index][1]++;
    }}
    break;\n"""
    controller.write(formattedFunctionStatement.format(functionName="addLine",
                                                       planString=generatePlanString(courseGroupList)))
    for plan in sequenceDict:
        controller.write(formattedAddLineSwitchStatement.format(planName=cleaner.cleanString(plan)))
    controller.write(switchEndString)

# Function that generates the switch statement and function removeLine
# Parameters:
#   sequenceDict - dict that maps plan name to a dict that represents the plan sequence
#   controller - file handle for controller.js file
def generateDeleteLineSwitch(sequenceDict, courseGroupList, controller):
    switchEndString = """    default:
    console.log("shouldn't be here");
    }
};\n"""
    formattedFunctionStatement = """this.{functionName} = function(line) {{
switch({planString}) {{ \n"""
    formmattedDeleteLineSwitchStatement = """ case "{planName}":
    var index = this.{planName}List.findIndex((element) => element[0] == line);
    if (index != -1) {{
        this.{planName}List[index][1]--
        if (this.{planName}List[index][1] <= 0) {{
            line.hide(false);
            this.{planName}List.splice(index, 1);
        }}
    }}
    break;"""
    controller.write(formattedFunctionStatement.format(functionName="removeLine",
                                                      planString=generatePlanString(courseGroupList)))

    for plan in sequenceDict:
        controller.write(formmattedDeleteLineSwitchStatement.format(planName=cleaner.cleanString(plan)))

    controller.write(switchEndString)

# Function that generates the switch statement associated with the addToClicked method
# Parameters:
#   sequenceDict - dict that maps plan name to a dict that represents the plan sequence
#   controller - file handle for controller.js file
def generateAddToClickSwitch(sequenceDict, courseGroupList, controller):
    switchEndString = """    default:
    console.log("shouldn't be here");
    }
};\n"""
    formattedFunctionStatement = """this.{functionName} = function(element, category) {{
switch({planString}) {{ \n"""
    formattedAddToClickStatement = """ case "{planName}":
    var index = this.{planName}Clicked.findIndex((item) => item[0] == element);
    if (index == -1) {{
        this.{planName}Clicked.push([element, category, 1]);
    }}
    else {{
        this.{planName}Clicked[index][1] = category;
        this.{planName}Clicked[index][2]++;
    }}
    this.{planName}ClickedMap.get(element).push(category);
    break;"""
    controller.write(formattedFunctionStatement.format(functionName="addToClicked",
                                                       planString=generatePlanString(courseGroupList)))
    for plan in sequenceDict:
        controller.write(formattedAddToClickStatement.format(planName=cleaner.cleanString(plan)))
    
    controller.write(switchEndString)

# Function that generates the switch statement associated with the deleteFromClicked method
# Parameters:
#   sequenceDict - dict that maps plan name to a dict that represents the plan sequence
#   controller - file handle for controller.js file
def generateDeleteFromClickSwitch(sequenceDict, courseGroupList, controller):
    switchEndString = """    default:
    console.log("shouldn't be here");
    }
};\n"""
    formattedFunctionStatement = """this.{functionName} = function(element, category) {{
switch({planString}) {{ \n"""
    formattedAddToClickStatement = """ case "{planName}":
    var index = this.{planName}Clicked.findIndex((item) => item[0] == element);
    if (index != -1) {{
        var indexMap = this.{planName}ClickedMap.get(element).lastIndexOf(category);
        if (indexMap != -1) {{
            this.{planName}ClickedMap.get(element).splice(indexMap, 1);
        }}
        this.{planName}Clicked[index][2]--;
        if (this.{planName}Clicked[index][2] <= 0) {{
            this.{planName}Clicked.splice(index, 1);
            return "";
        }}
        var maxIndex = this.{planName}ClickedMap.get(element).length - 1
        return this.{planName}ClickedMap.get(element)[maxIndex];
    }}
    return "";
    break;"""
    controller.write(formattedFunctionStatement.format(functionName="removeFromClicked",
                                                       planString=generatePlanString(courseGroupList)))
    for plan in sequenceDict:
        controller.write(formattedAddToClickStatement.format(planName=cleaner.cleanString(plan)))
    
    controller.write(switchEndString)

# Generates the clickable category legend. Allows a click to highlight all
# courses in that category.
# Parameters:
#   sequenceDict - dict that stores course objects
#       key - plan name
#       value - dict with term name as key and list of course objs in that plan & term
#   controller - file handle for controller.js file
def generateCategoryLegendJS(sequenceDict, courseGroupList, controller):
    # sort courses into categories and plans
    categoriesDict = sortIntoCategories(sequenceDict)

    # generate flags & listeners
    generateHighlightCategoryFlags(categoriesDict, controller)
    generateCategoryListeners(categoriesDict, courseGroupList, controller)
       
    formattedFunctionStatement = """this.{functionName} = function(categoryName, planName) {{
switch(categoryName) {{ \n"""

    controller.write(formattedFunctionStatement.format(functionName="highlightCategory"))

    # switch statement between categories for highlight category
    generateCategorySwitch(categoriesDict, controller, True)

    controller.write(formattedFunctionStatement.format(functionName="unhighlightCategory"))

     # switch statement between categories for unhighlight category
    generateCategorySwitch(categoriesDict, controller, False)

# Finds all of the legend buttons in all categories & plans. Writes the js that
# pushes these button elements to a list storing all buttons in that plan.
# eg: TraditionalPlanLegendBtns is a list that holds all legend button elements in
# the Traditional Plan
# Parameters:
#   categoriesDict - dict storing course objects
#       key - category name (eg: MATH)
#       value - dict with key as plan name, value as course object
#   sequenceDict - dict that maps plan name to a dict that represents the plan sequence
#   controller - file handle for controller.js file
def findLegendButtons(categoriesDict, sequenceDict, controller):
    # find the button in the doc
    formattedbtnStatement = """  var currbtn = document.getElementById("{categoryName}");\n"""
    # push the button element to a list
    formattedpushbtnStatement = """  that.{planName}LegendBtns.push(currbtn);\n"""

    for category in categoriesDict:
        # Note: categories are the same between all plans
        # Special cases to handle electives
        if category == "ComplementaryElective":
            controller.write(formattedbtnStatement.format(categoryName="COMP"))
        elif category == "ProgramTechnicalElective":
            controller.write(formattedbtnStatement.format(categoryName="PROG"))
        elif category == "ITSElective":
            controller.write(formattedbtnStatement.format(categoryName="ITS"))
        else:
            # not an elective
            controller.write(formattedbtnStatement.format(categoryName=category))

        for plan in sequenceDict:
            controller.write(formattedpushbtnStatement.format(planName=cleaner.cleanString(plan)))
    
# Sorts courses in sequenceDict into their categories.
# Parameters:
#   sequenceDict - dict that stores course objects
#       key - plan name
#       value - dict with term name as key and list of course objs in that plan & term
# Returns:
#   categoriesDict - dict storing course objects
#       key - category name (eg: MATH)
#       value - dict with key as plan name, value as course object
def sortIntoCategories(sequenceDict):
    categoriesDict = {}  # outer dict
    for plan in sequenceDict:
        for term in sequenceDict[plan]:
            for course in sequenceDict[plan][term]:
                mainCat = cleaner.cleanString(course.main_category)
                if mainCat == "":
                    # course does not have a category, not useful to include
                    continue
                subCatList = course.sub_categories
                cleanplan = cleaner.cleanString(plan)
                interdict = {}  # inner dict
                interdict[cleanplan] = [course]
                if mainCat not in categoriesDict.keys():
                    # category not seen yet, add new category
                    categoriesDict[mainCat] = interdict
                else:
                    # category is present in dict
                    if cleanplan not in categoriesDict[mainCat].keys():
                        # category taken but plan not seen yet
                        # keep existing categories but add a new plan (add new key to inner dict)
                        categoriesDict[mainCat].update(interdict)
                    else:
                        # category and plan both seen, can just append to corresponding list
                        categoriesDict[mainCat][cleanplan].append(course)
                for uncleanSubCat in subCatList:
                    interdict = {}  # inner dict
                    interdict[cleanplan] = [course]
                    subCat = cleaner.cleanString(uncleanSubCat)
                    if subCat == "":
                        # course does not have a category, not useful to include
                        continue
                    if subCat not in categoriesDict.keys():
                        # category not seen yet, add new category
                        categoriesDict[subCat] = interdict
                    else:
                        # category is present in dict
                        if cleanplan not in categoriesDict[subCat].keys():
                            # category taken but plan not seen yet
                            # keep existing categories but add a new plan (add new key to inner dict)
                            categoriesDict[subCat].update(interdict)
                        else:
                            # category and plan both seen, can just append to corresponding list
                            categoriesDict[subCat][cleanplan].append(course)
    
    return categoriesDict

# Function that generates the flags used to control the state of the category click buttons
# Parameters:
#   categoriesDict - dict storing course objects
#       key - category name (eg: MATH)
#       value - dict with key as plan name, value as course object
#   controller - file handle to controller.js
def generateHighlightCategoryFlags(categoriesDict, controller):
    formattedCategoriesFlagStatement = """var {categoryName}{planName}flag = false;\n"""
    for category in categoriesDict:
        if category == "": 
            continue
        for plan in categoriesDict[category]:
            if category == "ComplementaryElective":
                controller.write(formattedCategoriesFlagStatement.format(categoryName = "COMP", 
                                                                     planName = cleaner.cleanString(plan)))
            elif category == "ProgramTechnicalElective":
                controller.write(formattedCategoriesFlagStatement.format(categoryName = "PROG", 
                                                                     planName = cleaner.cleanString(plan)))
            elif category == "ITSElective":
                controller.write(formattedCategoriesFlagStatement.format(categoryName = "ITS", 
                                                                     planName = cleaner.cleanString(plan)))
            else:
                controller.write(formattedCategoriesFlagStatement.format(categoryName = cleaner.cleanString(category), 
                                                                     planName = cleaner.cleanString(plan)))

# Function that generates the click listeners for the category legend buttons
# Parameters:
#   categoriesDict - dict storing course objects
#       key - category name (eg: MATH)
#       value - dict with key as plan name, value as course object
#   courseGroupList - list of course groups taken in this program
#   controller - file handle to controller.js
def generateCategoryListeners(categoriesDict, courseGroupList, controller):
    # Get the element for the clicked legend button, check if the button is in the
    # pressed or unpressed state.
    # If in the unpressed state: highlight courses in that category, set the
    # class of the button to "-pressed", & update flags
    # If in the pressed state: unhighlight courses in that category, remove
    # "-pressed" from the button class, & update flags
    formattedCategoriesListener = """$scope.{categoryName}clickListener = function() {{
    var planName = {planString};
    var pressedbtn = document.getElementById("{categoryNameId}");
    var checkFlag = "!{categoryName}" + planName + "flag";
    var flagBool = eval(checkFlag);
    if (flagBool) {{
        that.highlightCategory("{categoryName}", planName);
        if (pressedbtn.classList.contains("legendbutton")) {{
            pressedbtn.classList.remove("legendbutton");
        }}
        pressedbtn.classList.add("legendbutton-pressed");
        var addClick = "that." + planName + "LegendBtnsClicked.push(pressedbtn)";
        eval(addClick);
        var flagName = "{categoryName}" + planName + "flag";
        eval(flagName + " = true");
    }}
    else {{
        that.unhighlightCategory("{categoryName}", planName);
        if (pressedbtn.classList.contains("legendbutton-pressed")) {{
            pressedbtn.classList.remove("legendbutton-pressed");
        }}
        pressedbtn.classList.add("legendbutton");
        var findIndex = "var index = that." + planName + "LegendBtnsClicked.findIndex((element) => element[0] == pressedbtn)";
        eval(findIndex);
        var removeClick = "that." + planName + "LegendBtnsClicked.splice(index, 1)";
        eval(removeClick);
        var flagName = "{categoryName}" + planName + "flag";
        eval(flagName + " = false");
    }}\n"""
    for category in categoriesDict:
        # special cases to handle electives, category is not the same as ID
        if category == "ComplementaryElective":
            controller.write(formattedCategoriesListener.format(categoryName="COMP", 
                                                                categoryNameId="COMP",
                                                                planString=generatePlanString(courseGroupList)))
        elif category == "ProgramTechnicalElective":
            controller.write(formattedCategoriesListener.format(categoryName="PROG", 
                                                                categoryNameId="PROG",
                                                                planString=generatePlanString(courseGroupList)))
        elif category == "ITSElective":
            controller.write(formattedCategoriesListener.format(categoryName="ITS", 
                                                                categoryNameId="ITS",
                                                                planString=generatePlanString(courseGroupList)))
        else:
            # not an elective
            controller.write(formattedCategoriesListener.format(categoryName=category, 
                                                                categoryNameId=category,
                                                                planString=generatePlanString(courseGroupList)))
        controller.write("}\n")

# Function that generates the switch statement to switch between categories within highlight
# or unhighlight function
# Parameters:
#   - categoriesDict: dict that maps categories to a dict of plans which contain courses within
#   that category
#   - controller: file handle to controller.js
#   - highlight: flag indicating if it is highlighting or unhighlighting 
#   (True for highlighting)  
def generateCategorySwitch(categoriesDict, controller, highlight):
    # outer switch between categories
    switchEndString = """break;   default:
    console.log("shouldn't be here");
    }
};\n"""
    formattedCaseCat = """  case "{categoryName}":\n"""
    for category in categoriesDict:
        if cleaner.cleanString(category) == "ComplementaryElective":
            controller.write(formattedCaseCat.format(categoryName="COMP"))
        if cleaner.cleanString(category) == "ProgramTechnicalElective":
            controller.write(formattedCaseCat.format(categoryName="PROG"))
        if cleaner.cleanString(category) == "ITSElective":
            controller.write(formattedCaseCat.format(categoryName="ITS"))
        else:
            controller.write(formattedCaseCat.format(categoryName=cleaner.cleanString(category)))
        generatePlanSwitch(categoriesDict[category], controller, highlight)
        controller.write("""       }\n""")
        controller.write("""      break;\n""")
    controller.write(switchEndString)

# Function that generates the switch statement to switch between plans within highlight
# or unhighlight function for a specific category
# Parameters:
#   - planDict: dict that maps plans to courses in that category
#   - controller: file handle to controller.js
#   - highlight: flag indicating if it is highlighting or unhighlighting 
#   (True for highlighting)  
def generatePlanSwitch(planDict, controller, highlight):
    # inner switch between plans
    formattedCasePlan  = """      case "{planName}":\n"""
    controller.write("    switch(planName) {\n")
    for plan in planDict:
        controller.write(formattedCasePlan.format(planName=cleaner.cleanString(plan)))
        generateCourseStatements(planDict[plan], controller, plan, highlight)
        controller.write("""       break;\n""")

# Function that generates the highlight or unhighlight statements for a specfic categtory
# and plan
# Parameters:
#   - courseList: list of course objects in that category for that plan
#   - controller: file handle to controller.js
#   - plan: name of current plan
#   - highlight: flag indicating if it is highlighting or unhighlighting 
#   (True for highlighting)      
def generateCourseStatements(courseList, controller, plan, highlight):
    for course in courseList:
        # special cases to handle electives
        if course.name == "Complementary Elective":
            if highlight:
                generateElectiveHighlightStatement("COMP", 
                                                   "ComplementaryElective", 
                                                    plan,  
                                                    controller)
            else:
                generateElectiveUnhighlightStatement("COMP", 
                                                   "ComplementaryElective", 
                                                    plan,  
                                                    controller)
            continue
        if course.name == "Program/Technical Elective":
            if highlight:
                generateElectiveHighlightStatement("PROG", 
                                                   "ProgramTechnicalElective", 
                                                    plan,  
                                                    controller)
            else:
                generateElectiveUnhighlightStatement("PROG", 
                                                   "ProgramTechnicalElective", 
                                                    plan, 
                                                    controller)
            continue
        if course.name == "ITS Elective":
            if highlight:
                generateElectiveHighlightStatement("ITS", 
                                                   "ITSElective", 
                                                   plan,  
                                                   controller)
            else:
                generateElectiveUnhighlightStatement("ITS", 
                                                   "ITSElective", 
                                                   plan,  
                                                   controller)
            continue
        # not an elective, fill in formatted statement with course attributes
        if highlight:
            generateNormalCourseHighlightStatement(course, plan, controller)
        else:
            generateNormalCourseUnhighlightStatement(course, plan, controller)

# Generates the statements needed to unhighlight a single elective when pressing
# the legend buttons
# Parameters:
#   - elective: shortend elective type
#   - longelective: long elective type
#   - plan: current plan
#   - counter: which number the current elective is
#   - controller: file handle to controller.js
def generateElectiveHighlightStatement(elective, longelective, plan, controller):
    formattedElectiveGetUnhighlightedElement = """        var {electiveName}elements = document.getElementsByClassName("{electiveName}");\n"""
    formattedElectivesHighlight = """        var i = 0;
        while ({electiveName}elements.length > 0) {{
          var currelement = document.getElementById({electiveName}elements.item(0).id);
          if (this.{planName}ClickedMap.get("{longElectiveName}{planName}" + i).length > 0) {{
                var mapLen = this.{planName}ClickedMap.get("{longElectiveName}{planName}" + i).length - 1
                var prevCate = this.{planName}ClickedMap.get("{longElectiveName}{planName}" + i)[mapLen];
                this.unHighlightElement(currelement, prevCate);
          }}
          this.highlightElement(currelement, categoryName);
          this.addToClicked("{longElectiveName}{planName}" + i, categoryName);
          i = i + 1;
        }}\n"""
    controller.write(formattedElectiveGetUnhighlightedElement.format(electiveName=elective))
    controller.write(formattedElectivesHighlight.format(electiveName=elective, 
                                                    longElectiveName=longelective, 
                                                    planName=plan, 
                                                    categoryName=elective))

# Generates the statements needed to unhighlight a single elective when pressing
# the legend buttons
# Parameters:
#   - elective: shortend elective type
#   - longelective: long elective type
#   - plan: current plan
#   - counter: which number the current elective is
#   - controller: file handle to controller.js
def generateElectiveUnhighlightStatement(elective, longelective, plan, controller):
    formattedElectiveGetHighlightedElement = """        var {electiveName}elements = document.getElementsByClassName("{electiveName}-highlighted");\n"""
    formattedElectivesUnhighlight = """        var i = 0;        
        while ({electiveName}elements.length > 0) {{
          var currelement = document.getElementById({electiveName}elements.item(0).id);
          var prevCate = this.removeFromClicked("{longElectiveName}{planName}" + i, "{categoryName}");
                if (!currelement.classList.contains(categoryName+"-highlighted")) {{
                    return;
                }}
                else {{
                    this.unHighlightElement(currelement, categoryName);
                    if (prevCate != "") {{
                        this.highlightElement(currelement, prevCate);
                    }}
                }}      
          i = i + 1;
        }}\n"""
    controller.write(formattedElectiveGetHighlightedElement.format(electiveName=elective))
    controller.write(formattedElectivesUnhighlight.format(electiveName=elective, 
                                                        longElectiveName=longelective, 
                                                        planName=plan, 
                                                        categoryName=elective))

# Generates the statements needed to highlight a single normal course when pressing
# the legend buttons
# Parameters:
#   - course: course object
#   - plan: current plan
#   - category: category of course
#   - controller: file handle to controller.js
def generateNormalCourseHighlightStatement(course, plan, controller):
    formattedHighlightStatement = """ var element = document.getElementById("{courseName}{planName}");
                            if (this.{planName}ClickedMap.get("{courseName}{planName}").length > 0) {{
                                var mapLen = this.{planName}ClickedMap.get("{courseName}{planName}").length - 1
                                var prevCate = this.{planName}ClickedMap.get("{courseName}{planName}")[mapLen];
                                this.unHighlightElement(element, prevCate);
                            }}
                            this.highlightElement(element, categoryName);
                            this.addToClicked("{courseName}{planName}", categoryName);\n"""
    controller.write(formattedHighlightStatement.format(planName=cleaner.cleanString(plan),
                                                        courseName=cleaner.cleanString(course.name)))

# Generates the statements needed to unhighlight a single normal course when pressing
# the legend buttons
# Parameters:
#   - course: course object
#   - plan: current plan
#   - controller: file handle to controller.js
def generateNormalCourseUnhighlightStatement(course, plan, controller):
    formattedUnhighlightStatement = """     var element = document.getElementById("{courseName}{planName}");
                            var prevCate = this.removeFromClicked("{courseName}{planName}", categoryName);
                                if (element.classList.contains(categoryName+"-highlighted")) {{
                                    this.unHighlightElement(element, categoryName);
                                    if (prevCate != "") {{
                                        this.highlightElement(element, prevCate);
                                    }}
                                }}\n"""
    controller.write(formattedUnhighlightStatement.format(courseName=cleaner.cleanString(course.name),
                                                          planName=cleaner.cleanString(plan)))

# Function that generates the statement representing which plan is currently selected
# Parameters:
#   courseGroupList - list of all course groups taken that term
def generatePlanString(courseGroupList):
    planString = "$scope.selectedPlan"
    formattedCourseGroup = "$scope.field{number}.group{number}"
    for courseGroup in courseGroupList:
        planString += "+"+formattedCourseGroup.format(number=courseGroup)
    return planString

# Function that properly concludes and closes the controller JS
# Parameters:
#   controller - file handle for controller JS
def closeControllerJavaScript(controller):
    controller.write("});\n")
    writeRightClickDirective(controller)
    writeRadioChangeDirective(controller)
    controller.close()

# Function that appends the custom Angular directive used to handle right click
# events to the end of the controller JS file
# Parameters:
#   controller - file handle for controller JS
def writeRightClickDirective(controller):
    rightClickDirective = """app.directive('ngRightClick', function($parse) {
    return function(scope, element, attrs) {
        var fn = $parse(attrs.ngRightClick);
        element.bind('contextmenu', function(event) {
            scope.$apply(function() {
                event.preventDefault();
                fn(scope, {$event:event});
            });
        });
    };
    });"""
    controller.write(rightClickDirective)

# Function that appends the custom Angular directive used to handle radio input changing
# to the end of the controller JS file
# Parameters:
#   controller - file handle for controller JS
def writeRadioChangeDirective(controller):
    radioChangeDirective = """app.directive('ngChangeRadio', function($parse) {
    return function(scope, element, attrs) {
        var fn = $parse(attrs.ngChangeRadio);
        element.bind('change', function(event) {
            scope.$apply(function() {
                event.preventDefault();
                fn(scope, {$event:event});
            });
        });
    };
    });"""
    controller.write(radioChangeDirective)
    