import QtQuick 2.15
import QtQuick.Controls 2.15
import QtQuick.Layouts 1.15

Popup {
    id: settingsDialog
    width: 500
    height: 400
    modal: true
    anchors.centerIn: parent
    
    property var appController: null
    
    ColumnLayout {
        anchors.fill: parent
        anchors.margins: 10
        spacing: 15
        
        GroupBox {
            title: "API Configuration"
            Layout.fillWidth: true
            
            ColumnLayout {
                anchors.fill: parent
                spacing: 10
                
                Label {
                    text: "OpenRouter API Key:"
                }
                
                TextField {
                    id: apiKeyField
                    Layout.fillWidth: true
                    placeholderText: "Enter your OpenRouter API key..."
                    echoMode: TextInput.Password
                }
                
                Label {
                    text: "Base URL:"
                }
                
                TextField {
                    id: baseUrlField
                    Layout.fillWidth: true
                    text: "https://openrouter.ai/api/v1"
                }
            }
        }
        
        GroupBox {
            title: "Display Settings"
            Layout.fillWidth: true
            
            ColumnLayout {
                anchors.fill: parent
                spacing: 10
                
                RowLayout {
                    Label {
                        text: "Font Size:"
                    }
                    
                    SpinBox {
                        id: fontSizeSpinBox
                        from: 8
                        to: 24
                        value: 14
                    }
                }
            }
        }
        
        GroupBox {
            title: "File Sync"
            Layout.fillWidth: true
            
            ColumnLayout {
                anchors.fill: parent
                spacing: 10
                
                CheckBox {
                    id: fileSyncEnabled
                    text: "Enable file synchronization"
                }
                
                RowLayout {
                    enabled: fileSyncEnabled.checked
                    
                    TextField {
                        id: fileSyncPath
                        Layout.fillWidth: true
                        placeholderText: "Path to sync file..."
                    }
                    
                    Button {
                        text: "Browse"
                        onClicked: {
                            // File dialog would be implemented here
                        }
                    }
                }
            }
        }
        
        Item {
            Layout.fillHeight: true
        }
        
        RowLayout {
            Layout.fillWidth: true
            
            Button {
                text: "Test Connection"
                enabled: apiKeyField.text.trim().length > 0
                onClicked: {
                    // Test API connection
                }
            }
            
            Item { Layout.fillWidth: true }
            
            Button {
                text: "Cancel"
                onClicked: settingsDialog.close()
            }
            
            Button {
                text: "Save"
                enabled: apiKeyField.text.trim().length > 0
                onClicked: {
                    // Save settings
                    if (appController) {
                        // This would need to be implemented
                    }
                    settingsDialog.close()
                }
            }
        }
    }
}