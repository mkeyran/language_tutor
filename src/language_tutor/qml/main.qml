import QtQuick 2.15
import QtQuick.Controls 2.15
import QtQuick.Layouts 1.15
import QtQuick.Window 2.15
import "dialogs"

ApplicationWindow {
    id: window
    width: 1000
    height: 700
    visible: true
    title: "Language Tutor"

    // App controller will be set from C++ side as context property

    menuBar: MenuBar {
        Menu {
            title: "&File"
            
            MenuItem {
                text: "&Save State\tCtrl+Alt+S"
                onTriggered: appController.saveState()
            }
            
            MenuItem {
                text: "&Load State\tCtrl+Alt+L"
                onTriggered: appController.loadState()
            }
            
            MenuItem {
                text: "&Export Markdown\tCtrl+Alt+E"
                onTriggered: appController.exportMarkdown()
            }
            
            MenuSeparator { }
            
            MenuItem {
                text: "E&xit\tCtrl+Q"
                onTriggered: Qt.quit()
            }
        }
        
        Menu {
            title: "&Tools"
            
            MenuItem {
                text: "&Ask AI\tCtrl+G"
                onTriggered: qaDialog.open()
            }
            
            MenuItem {
                text: "&Lookup Word\tCtrl+D"
                onTriggered: wiktionaryDialog.open()
            }
            
            MenuItem {
                text: "&Settings\tCtrl+,"
                onTriggered: settingsDialog.open()
            }
        }
    }

    SplitView {
        id: mainSplitter
        anchors.fill: parent
        orientation: Qt.Horizontal

        // Left pane - Exercise generation
        Rectangle {
            id: leftPane
            SplitView.minimumWidth: 250
            SplitView.preferredWidth: 300
            color: "#f5f5f5"

            ColumnLayout {
                anchors.fill: parent
                anchors.margins: 10
                spacing: 10

                GroupBox {
                    id: selectionGroup
                    title: "Exercise Settings"
                    Layout.fillWidth: true

                    GridLayout {
                        anchors.fill: parent
                        columns: 2
                        columnSpacing: 10
                        rowSpacing: 5

                        Label { text: "Language:" }
                        ComboBox {
                            id: languageSelect
                            Layout.fillWidth: true
                            model: appController.languageModel
                            textRole: "name"
                            valueRole: "code"
                            onCurrentValueChanged: {
                                if (currentValue)
                                    appController.setLanguage(currentValue)
                            }
                        }

                        Label { text: "Level:" }
                        ComboBox {
                            id: levelSelect
                            Layout.fillWidth: true
                            model: appController.levelModel
                            textRole: "name"
                            valueRole: "code"
                            onCurrentValueChanged: {
                                if (currentValue)
                                    appController.setLevel(currentValue)
                            }
                        }

                        Label { text: "Exercise Type:" }
                        ComboBox {
                            id: exerciseSelect
                            Layout.fillWidth: true
                            model: appController.exerciseTypeModel
                            textRole: "name"
                            valueRole: "code"
                            onCurrentValueChanged: {
                                if (currentValue)
                                    appController.setExerciseType(currentValue)
                            }
                        }

                        Button {
                            id: generateBtn
                            text: appController.generateButtonText
                            enabled: appController.generateButtonEnabled
                            Layout.columnSpan: 2
                            Layout.fillWidth: true
                            onClicked: appController.generateExercise()
                        }
                    }
                }

                GroupBox {
                    title: "Generated Exercise"
                    Layout.fillWidth: true
                    Layout.fillHeight: true

                    ColumnLayout {
                        anchors.fill: parent
                        spacing: 5

                        Label {
                            text: "Exercise:"
                            font.bold: true
                        }
                        
                        ScrollView {
                            Layout.fillWidth: true
                            Layout.preferredHeight: 120
                            
                            TextArea {
                                id: exerciseDisplay
                                text: appController.generatedExercise
                                readOnly: !appController.isCustomExercise
                                placeholderText: "Exercise will appear here..."
                                wrapMode: TextArea.Wrap
                                selectByMouse: true
                                onTextChanged: {
                                    if (!readOnly && text !== appController.generatedExercise)
                                        appController.setCustomExercise(text)
                                }
                            }
                        }

                        Label {
                            text: "Hints:"
                            font.bold: true
                        }
                        
                        ScrollView {
                            Layout.fillWidth: true
                            Layout.fillHeight: true
                            
                            TextArea {
                                id: hintsDisplay
                                text: appController.generatedHints
                                readOnly: true
                                placeholderText: "Hints will appear here..."
                                wrapMode: TextArea.Wrap
                                selectByMouse: true
                            }
                        }
                    }
                }
            }
        }

        // Right pane - Writing check
        Rectangle {
            id: rightPane
            SplitView.fillWidth: true
            color: "#f5f5f5"

            ColumnLayout {
                anchors.fill: parent
                anchors.margins: 10
                spacing: 10

                GroupBox {
                    title: "Your Writing"
                    Layout.fillWidth: true
                    Layout.fillHeight: true

                    ColumnLayout {
                        anchors.fill: parent
                        spacing: 5

                        ScrollView {
                            Layout.fillWidth: true
                            Layout.fillHeight: true
                            
                            TextArea {
                                id: writingInput
                                text: appController.writingInput
                                placeholderText: "Write your text here..."
                                wrapMode: TextArea.Wrap
                                selectByMouse: true
                                onTextChanged: {
                                    if (text !== appController.writingInput)
                                        appController.setWritingInput(text)
                                }
                                
                                Keys.onPressed: {
                                    if (event.key === Qt.Key_Return && event.modifiers & Qt.ControlModifier) {
                                        appController.checkWriting()
                                        event.accepted = true
                                    }
                                }
                            }
                        }

                        RowLayout {
                            Layout.fillWidth: true
                            
                            Button {
                                id: checkBtn
                                text: appController.checkButtonText
                                enabled: appController.checkButtonEnabled
                                Layout.fillWidth: true
                                onClicked: appController.checkWriting()
                            }
                            
                            Label {
                                id: wordCountLabel
                                text: appController.wordCountText
                                color: appController.wordCountColor
                            }
                        }
                    }
                }

                GroupBox {
                    title: "Feedback"
                    Layout.fillWidth: true
                    Layout.fillHeight: true

                    TabBar {
                        id: feedbackTabs
                        width: parent.width
                        
                        TabButton { text: "Mistakes" }
                        TabButton { text: "Stylistic Errors" }
                        TabButton { text: "Recommendations" }
                    }

                    StackLayout {
                        anchors.top: feedbackTabs.bottom
                        anchors.bottom: parent.bottom
                        anchors.left: parent.left
                        anchors.right: parent.right
                        anchors.margins: 5
                        currentIndex: feedbackTabs.currentIndex

                        ScrollView {
                            TextArea {
                                text: appController.writingMistakes
                                readOnly: true
                                wrapMode: TextArea.Wrap
                                selectByMouse: true
                                textFormat: TextArea.RichText
                            }
                        }

                        ScrollView {
                            TextArea {
                                text: appController.styleErrors
                                readOnly: true
                                wrapMode: TextArea.Wrap
                                selectByMouse: true
                                textFormat: TextArea.RichText
                            }
                        }

                        ScrollView {
                            TextArea {
                                text: appController.recommendations
                                readOnly: true
                                wrapMode: TextArea.Wrap
                                selectByMouse: true
                                textFormat: TextArea.RichText
                            }
                        }
                    }
                }
            }
        }
    }

    // Dialogs
    QADialog {
        id: qaDialog
        appController: window.appController
    }

    SettingsDialog {
        id: settingsDialog
        appController: window.appController
    }

    WiktionaryDialog {
        id: wiktionaryDialog
        appController: window.appController
    }

    // Status bar
    footer: Rectangle {
        height: 25
        color: "#e0e0e0"
        border.color: "#c0c0c0"
        border.width: 1

        Label {
            anchors.left: parent.left
            anchors.verticalCenter: parent.verticalCenter
            anchors.margins: 5
            text: appController.statusMessage
        }
    }
}