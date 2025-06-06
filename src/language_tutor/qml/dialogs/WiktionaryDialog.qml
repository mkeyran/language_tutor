import QtQuick 2.15
import QtQuick.Controls 2.15
import QtQuick.Layouts 1.15

Popup {
    id: wiktionaryDialog
    width: 500
    height: 400
    modal: true
    anchors.centerIn: parent
    
    property var appController: null
    property string currentLanguage: "en"
    
    ColumnLayout {
        anchors.fill: parent
        anchors.margins: 10
        spacing: 10
        
        Label {
            text: "Look up a word in Wiktionary:"
            font.bold: true
        }
        
        RowLayout {
            Layout.fillWidth: true
            
            TextField {
                id: wordInput
                Layout.fillWidth: true
                placeholderText: "Enter word to look up..."
                selectByMouse: true
                onAccepted: lookupButton.clicked()
            }
            
            Button {
                id: lookupButton
                text: "Lookup"
                enabled: wordInput.text.trim().length > 0
                onClicked: {
                    if (wordInput.text.trim().length > 0) {
                        var word = wordInput.text.trim()
                        var url = buildWiktionaryUrl(word, currentLanguage)
                        resultLabel.text = "Wiktionary URL: " + url
                        // In a real implementation, this would open in a web view
                        // or external browser
                    }
                }
            }
        }
        
        Label {
            id: resultLabel
            Layout.fillWidth: true
            text: "Enter a word and click Lookup to get the Wiktionary URL"
            wrapMode: Text.Wrap
        }
        
        Item {
            Layout.fillHeight: true
        }
        
        RowLayout {
            Layout.fillWidth: true
            
            Item { Layout.fillWidth: true }
            
            Button {
                text: "Close"
                onClicked: wiktionaryDialog.close()
            }
        }
    }
    
    function buildWiktionaryUrl(word, language) {
        // Simple URL building - in real implementation this would use
        // the utility function from the Python backend
        var baseUrl = "https://en.wiktionary.org/wiki/"
        return baseUrl + encodeURIComponent(word)
    }
}