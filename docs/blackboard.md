# Blackboard exam set-up instructions

Check that no-one has permissions on the unit who should be there: all teaching assistants should be changed to _limited teaching assistant_ for example, especially undergraduates, otherwise they can see the exam.

Under _Course Tools / Tests, Surveys and Pools_ go to _Pools_ and upload the ZIP of the exam this imports the pools of questions.

Under _Tests_, create a test as follows:

  * _Every student takes the same exam_: Select _Reuse Question > Find Questions_ and import all the questions. When deploying the test, keep _Randomise Questions_ off.
  * _Same questions but random order for each student_: Same as above but turn _Randomise Questions_ on (this allows the questions to be shuffled even if they are not all worth the same number of points).
  * _Students get different questions_: Select _Reuse Question > Create Random Block_ and create a random block for each section of the exam where students each get K randomly chosen questions out of N. In the block window, first tick the box next to the pool to use, then select the _All Pool Questions_ radio button, then OK. Set _Number of Questions_ for each block to the correct K (N is always the block size) and set the _Points per question_ correctly.

Random blocks also allow you to do a test where first everyone gets all easy questions in a random order, then all hard ones - as long as the easy questions are all worth the same number of points, and the same for the hard ones (though hard questions can be worth more points than easy ones).

To deploy a test, use _Assessment > Test_ on a content block (normal page type on blackboard). Under test options,

  - Keep _Make available_ on _No_ unless you want to release the test to students immediately.
  - _Multiple Attempts_ should not be ticked for an exam, but is ok for a formative test if desired.
  - _Force Completion_ should be off.
  - _Timer, Display After / Until_ need to be set correctly for exams.
  - _Test Availability Exceptions_ are where AEA get added, but this is for the school office to do.

To prevent early release of exam results:
  - Untick all boxes in _Show test results and feedback to students_, and set both dropdowns to _Choose_.
  - In the grade centre, hide the column created for this deployed test: _Grade Centre > Full Grade Centre_ in left menu, then _Hide from students (on/off)_ in the column heading dropdown. The column displays a circle with a strikethrough if it is hidden from students.

Under _Test Presentation_, the options are:
  - "Traditional" exam: radio box on _All at Once_ (does what it says).
  - For a "no going back" exam, select both the _One at a Time Prohibit Backtracking_ radio button and the tick box: the radio button is for _One at a Time_ and the tick box is _Prohibit Backtracking_. One for the UI hall of shame!

_Randomise Questions_ adds an additional layer of randomisation where all questions are presented in random order every time a student takes the test. You typically do not want this if you are using random blocks, the only time you'd want this is if you have only one question pool for all students but you want the questions in random order, even though they are not all worth the same number of marks.
