import sys
from PyQt5.QtWidgets import QApplication, QWidget, QInputDialog, QMessageBox

class Human():
    def __init__(self):
        self.question = "No question asked yet"
        self.answer = "No answer given yet"  

    def get_past_input(self):
        # combine the question and answer
        return "Question: " + self.question + "\nAnswer: " + self.answer

    def ask_question(self, question):
        self.question = question
        self.answer = self.ask_question_UI(question)
        return self.answer

    def ask_action(self, action):
        self.ask_action_UI(action)

    def ask_question_UI(self, question):  
        app = QApplication(sys.argv)
        answer, ok = QInputDialog.getText(None, "Question", question)
        if not ok:  # User closed the dialog window  
            return "No answer provided"  
        return answer

    def ask_action_UI(self, action):
        app = QApplication(sys.argv)
        QMessageBox.information(None, "Action:", action + "\n\nClick OK when you have completed the action")

    def ask_action_API(self, action):
        # TODO
        pass

    def ask_question_API(self, question):
        # TODO
        pass


def main():  
    human = Human()  
    question = "What is the capital of France?"  
    answer = human.ask_question(question)  
    print("Answer:", answer)  
    action = "Open the browser"  
    human.ask_action(action)  
    print("Action completed")

if __name__ == "__main__":  
    main()
