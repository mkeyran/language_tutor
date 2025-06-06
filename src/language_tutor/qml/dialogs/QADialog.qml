import QtQuick 2.15
import QtQuick.Controls 2.15
import QtQuick.Layouts 1.15

Popup {
    id: qaDialog
    width: 600
    height: 500
    modal: true
    anchors.centerIn: parent
    
    property var appController: null
    
    ColumnLayout {
        anchors.fill: parent
        anchors.margins: 10
        spacing: 10
        
        Label {
            text: "Ask a question about the current exercise:"
            font.bold: true
        }
        
        ScrollView {
            Layout.fillWidth: true
            Layout.preferredHeight: 100
            
            TextArea {
                id: questionInput
                placeholderText: "Type your question here..."
                wrapMode: TextArea.Wrap
                selectByMouse: true
            }
        }
        
        Button {
            id: askButton
            text: "Ask AI"
            Layout.fillWidth: true
            enabled: questionInput.text.trim().length > 0
            onClicked: {
                if (appController) {
                    // This would need to be implemented in the app controller
                    answerDisplay.text = "Feature coming soon..."
                }
            }
        }
        
        Label {
            text: "Answer:"
            font.bold: true
        }
        
        ScrollView {
            Layout.fillWidth: true
            Layout.fillHeight: true
            
            TextArea {
                id: answerDisplay
                readOnly: true
                wrapMode: TextArea.Wrap
                selectByMouse: true
                placeholderText: "Answer will appear here..."
            }
        }
        
        RowLayout {
            Layout.fillWidth: true
            
            Button {
                text: "Clear"
                onClicked: {
                    questionInput.text = ""
                    answerDisplay.text = ""
                }
            }
            
            Item { Layout.fillWidth: true }
            
            Button {
                text: "Close"
                onClicked: qaDialog.close()
            }
        }
    }
}