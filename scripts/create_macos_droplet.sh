#!/bin/bash
# Script to create a macOS Automator droplet for DreamBooth training

cat << 'EOF' > ~/Desktop/DreamBoothDroplet.workflow
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>AMApplicationBuild</key>
    <string>523</string>
    <key>AMApplicationVersion</key>
    <string>2.10</string>
    <key>AMDocumentVersion</key>
    <string>2</string>
    <key>actions</key>
    <array>
        <dict>
            <key>action</key>
            <dict>
                <key>AMAccepts</key>
                <dict>
                    <key>Container</key>
                    <string>List</string>
                    <key>Optional</key>
                    <false/>
                    <key>Types</key>
                    <array>
                        <string>com.apple.cocoa.path</string>
                    </array>
                </dict>
                <key>AMActionVersion</key>
                <string>1.1.2</string>
                <key>AMApplication</key>
                <array>
                    <string>Finder</string>
                </array>
                <key>AMParameterProperties</key>
                <dict>
                    <key>itemType</key>
                    <dict/>
                </dict>
                <key>AMProvides</key>
                <dict>
                    <key>Container</key>
                    <string>List</string>
                    <key>Types</key>
                    <array>
                        <string>com.apple.cocoa.path</string>
                    </array>
                </dict>
                <key>ActionBundlePath</key>
                <string>/System/Library/Automator/Filter Finder Items.action</string>
                <key>ActionName</key>
                <string>Filter Finder Items</string>
                <key>ActionParameters</key>
                <dict>
                    <key>itemType</key>
                    <string>com.apple.cocoa.path</string>
                    <key>predicate</key>
                    <data>
                    YnBsaXN0MDDUAQIDBAUGVVZYJHZlcnNpb25YJG9iamVjdHNZJGFyY2hpdmVyVCR0b3ASAAGGoK8QEgcIDxQcJicpMDQ4PD9DR0tPUlUkbnVsbNMJCgsMDQ5XTlMua2V5c1pOUy5vYmplY3RzViRjbGFzc6IMgQGAEqINgQKAEdIQERITWiRjbGFzc25hbWVYJGNsYXNzZXNeTlNNdXRhYmxlQXJyYXmiElVOU0FycmF50hARFRZeTlNNdXRhYmxlQXJyYXmiFRPVFxgZGhobWU5TT3BlcmFuZFxOU1JpZ2h0RXhwcmVzc2lvbl8QEE5TTGVmdEV4cHJlc3Npb25ZTlNPcHRpb25zgQOAEIEPgAXSEB0eH1okY2xhc3NuYW1lWCRjbGFzc2VzXxATTlNLZXlQYXRoRXhwcmVzc2lvbqMgISJfEBNOU0tleVBhdGhFeHByZXNzaW9uXE5TRXhwcmVzc2lvblhOU09iamVjdNIjJB4lWU5TS2V5UGF0aIAEXxAPa0lNYWdlTmFtZUVxdWFsc9IdKCJeTlNDb25zdGFudFZhbHVloCLTGiorLC0uXE5TUHJlZGljYXRlXxAQTlNSaWdodEV4cHJlc3Npb25ZTlNPcGVyYXRvcltOU0xlZnRFeHByZXNzaW9ugAaADoEOgAfYMBkxCTIRMxobNTY3Wk5TT3BlcmFuZFpOU01vZGlmaWVyWk5TT3B0aW9uc1lOU0tleVBhdGgQBBAAgAiBCFd0eXBlSUTSHRghoiHA0h09JD9ZTlMuc3RyaW5ngAlbcHVibGljLmpwZWfSEB1BQl8QFU5TQ29uc3RhbnRWYWx1ZUV4cHJlc3Npb26jQ0QiXxAVTlNDb25zdGFudFZhbHVlRXhwcmVzc2lvbtIdRiJcTlNDb25zdGFudFZhbHVloCLYMBkxCTIRSBs2SjdaTlNPcGVyYW5kWk5TTW9kaWZpZXJaTlNPcHRpb25zWU5TS2V5UGF0aBACEACACYEKgArSHT0kTYALW3B1YmxpYy5qcGVn0hARUFFfEBVOU0NvbXBhcmlzb25QcmVkaWNhdGWiUCLSEBFTVFxOU0V4cHJlc3Npb26iUyIACAARABoAJAApADIANwBJAEwAUQBTAGAAZgBtAHQAfwCGAJIAlACWAJgAnQCfAKEAowCwAMAAzQDaAOcA+wEAAQ8BEQETARgBHQElATABMgE0ATkBRAFPAWMBaAFqAWwBbgFzAXgBgQGJAY4BkwGcAa8BuAHLAdAB1QHXAdkB2wHdAd8B5AHpAe4CBQIIAH4CgAKCAoQCiQKOApMCqgKsAq4CsAK1AscC2ALqAu8DAQMGA6kAAAAAAAACAQAAAAAAAABWAAAAAAAAAAAAAAAAAAADsQ==
                    </data>
                </dict>
                <key>BundleIdentifier</key>
                <string>com.apple.Automator.Filter_Finder_Items</string>
                <key>CFBundleVersion</key>
                <string>1.1.2</string>
                <key>CanShowSelectedItemsWhenRun</key>
                <true/>
                <key>CanShowWhenRun</key>
                <true/>
                <key>Category</key>
                <array>
                    <string>AMCategoryFilesAndFolders</string>
                </array>
                <key>Class Name</key>
                <string>Filter_Finder_Items</string>
                <key>InputUUID</key>
                <string>B4F4C9A6-9E3F-4A5E-8D1A-3B2C6D8E9F0A</string>
                <key>Keywords</key>
                <array/>
                <key>OutputUUID</key>
                <string>C5F5D0B7-0F4F-4B6F-9E2A-4C3D7E8F0A1B</string>
                <key>ShowWhenRun</key>
                <false/>
                <key>UUID</key>
                <string>D6F6E1C8-1F5F-4C7F-0E3B-5D4E8F9A0B2C</string>
                <key>UnlocalizedApplications</key>
                <array>
                    <string>Finder</string>
                </array>
                <key>arguments</key>
                <dict>
                    <key>0</key>
                    <dict>
                        <key>default value</key>
                        <string>com.apple.cocoa.path</string>
                        <key>name</key>
                        <string>itemType</string>
                        <key>required</key>
                        <string>0</string>
                        <key>type</key>
                        <string>0</string>
                        <key>uuid</key>
                        <string>0</string>
                    </dict>
                </dict>
                <key>isViewVisible</key>
                <false/>
                <key>location</key>
                <string>309.000000:358.000000</string>
                <key>nibPath</key>
                <string>/System/Library/Automator/Filter Finder Items.action/Contents/Resources/Base.lproj/main.nib</string>
            </dict>
            <key>isViewVisible</key>
            <false/>
        </dict>
        <dict>
            <key>action</key>
            <dict>
                <key>AMAccepts</key>
                <dict>
                    <key>Container</key>
                    <string>List</string>
                    <key>Optional</key>
                    <true/>
                    <key>Types</key>
                    <array>
                        <string>com.apple.cocoa.string</string>
                    </array>
                </dict>
                <key>AMActionVersion</key>
                <string>2.0.3</string>
                <key>AMApplication</key>
                <array>
                    <string>Automator</string>
                </array>
                <key>AMParameterProperties</key>
                <dict>
                    <key>COMMAND_STRING</key>
                    <dict/>
                    <key>CheckedForUserDefaultShell</key>
                    <dict/>
                    <key>inputMethod</key>
                    <dict/>
                    <key>shell</key>
                    <dict/>
                    <key>source</key>
                    <dict/>
                </dict>
                <key>AMProvides</key>
                <dict>
                    <key>Container</key>
                    <string>List</string>
                    <key>Types</key>
                    <array>
                        <string>com.apple.cocoa.string</string>
                    </array>
                </dict>
                <key>ActionBundlePath</key>
                <string>/System/Library/Automator/Run Shell Script.action</string>
                <key>ActionName</key>
                <string>Run Shell Script</string>
                <key>ActionParameters</key>
                <dict>
                    <key>COMMAND_STRING</key>
                    <string>#!/bin/bash

# DreamBooth Training Droplet
# Drop images here to start training

# Get the dropped files
IMAGES=("$@")
IMAGE_COUNT=${#IMAGES[@]}

# Check if we have enough images
if [ $IMAGE_COUNT -lt 3 ]; then
    osascript -e 'display alert "Not enough images" message "Please drop at least 3-5 images for training." as critical'
    exit 1
fi

# Ask for subject type
SUBJECT=$(osascript -e 'set subjectType to text returned of (display dialog "What type of subject are you training?" default answer "dog" buttons {"Cancel", "OK"} default button "OK")')

# Ask for trigger word
TRIGGER=$(osascript -e 'set triggerWord to text returned of (display dialog "Enter trigger word (or use default):" default answer "sks" buttons {"Cancel", "OK"} default button "OK")')

# Create temporary directory
TEMP_DIR=$(mktemp -d)
mkdir -p "$TEMP_DIR/images"

# Copy images
for i in "${!IMAGES[@]}"; do
    cp "${IMAGES[$i]}" "$TEMP_DIR/images/$(printf "%03d" $i).jpg"
done

# Create config
cat > "$TEMP_DIR/config.json" << EOL
{
  "model": "dev",
  "seed": 42,
  "steps": 20,
  "guidance": 3.0,
  "quantize": 4,
  "width": 512,
  "height": 512,
  "training_loop": {
    "num_epochs": 100,
    "batch_size": 1
  },
  "optimizer": {
    "name": "AdamW",
    "learning_rate": 1e-4
  },
  "save": {
    "output_path": "~/Desktop/dreambooth_${SUBJECT}_$(date +%Y%m%d_%H%M%S)",
    "checkpoint_frequency": 20
  },
  "instrumentation": {
    "plot_frequency": 5,
    "generate_image_frequency": 20,
    "validation_prompt": "photo of ${TRIGGER} ${SUBJECT}"
  },
  "lora_layers": {
    "single_transformer_blocks": {
      "block_range": {"start": 0, "end": 38},
      "layer_types": ["proj_out", "proj_mlp", "attn.to_q", "attn.to_k", "attn.to_v"],
      "lora_rank": 8
    }
  },
  "examples": {
    "path": "images/",
    "images": [
EOL

# Add image entries
for i in "${!IMAGES[@]}"; do
    if [ $i -gt 0 ]; then echo "," >> "$TEMP_DIR/config.json"; fi
    echo -n "      {\"image\": \"$(printf "%03d" $i).jpg\", \"prompt\": \"photo of ${TRIGGER} ${SUBJECT}\"}" >> "$TEMP_DIR/config.json"
done

# Close config
cat >> "$TEMP_DIR/config.json" << EOL

    ]
  }
}
EOL

# Show notification
osascript -e 'display notification "Starting DreamBooth training..." with title "DreamBooth"'

# Start training in Terminal
osascript -e "tell application \"Terminal\"
    activate
    do script \"cd '$TEMP_DIR' && mflux-train --train-config config.json\"
end tell"
</string>
                    <key>CheckedForUserDefaultShell</key>
                    <true/>
                    <key>inputMethod</key>
                    <integer>1</integer>
                    <key>shell</key>
                    <string>/bin/bash</string>
                    <key>source</key>
                    <string></string>
                </dict>
                <key>BundleIdentifier</key>
                <string>com.apple.RunShellScript</string>
                <key>CFBundleVersion</key>
                <string>2.0.3</string>
                <key>CanShowSelectedItemsWhenRun</key>
                <false/>
                <key>CanShowWhenRun</key>
                <true/>
                <key>Category</key>
                <array>
                    <string>AMCategoryUtilities</string>
                </array>
                <key>Class Name</key>
                <string>RunShellScriptAction</string>
                <key>InputUUID</key>
                <string>E7F8G9H0-1A2B-3C4D-5E6F-7890ABCDEF01</string>
                <key>Keywords</key>
                <array>
                    <string>Shell</string>
                    <string>Script</string>
                    <string>Command</string>
                    <string>Run</string>
                    <string>Unix</string>
                </array>
                <key>OutputUUID</key>
                <string>F8G9H0A1-2B3C-4D5E-6F78-90ABCDEF0123</string>
                <key>UUID</key>
                <string>G9H0A1B2-3C4D-5E6F-7890-ABCDEF012345</string>
                <key>UnlocalizedApplications</key>
                <array>
                    <string>Automator</string>
                </array>
                <key>arguments</key>
                <dict>
                    <key>0</key>
                    <dict>
                        <key>default value</key>
                        <integer>0</integer>
                        <key>name</key>
                        <string>inputMethod</string>
                        <key>required</key>
                        <string>0</string>
                        <key>type</key>
                        <string>0</string>
                        <key>uuid</key>
                        <string>0</string>
                    </dict>
                    <key>1</key>
                    <dict>
                        <key>default value</key>
                        <string></string>
                        <key>name</key>
                        <string>source</string>
                        <key>required</key>
                        <string>0</string>
                        <key>type</key>
                        <string>0</string>
                        <key>uuid</key>
                        <string>1</string>
                    </dict>
                    <key>2</key>
                    <dict>
                        <key>default value</key>
                        <false/>
                        <key>name</key>
                        <string>CheckedForUserDefaultShell</string>
                        <key>required</key>
                        <string>0</string>
                        <key>type</key>
                        <string>0</string>
                        <key>uuid</key>
                        <string>2</string>
                    </dict>
                    <key>3</key>
                    <dict>
                        <key>default value</key>
                        <string></string>
                        <key>name</key>
                        <string>COMMAND_STRING</string>
                        <key>required</key>
                        <string>0</string>
                        <key>type</key>
                        <string>0</string>
                        <key>uuid</key>
                        <string>3</string>
                    </dict>
                    <key>4</key>
                    <dict>
                        <key>default value</key>
                        <string>/bin/sh</string>
                        <key>name</key>
                        <string>shell</string>
                        <key>required</key>
                        <string>0</string>
                        <key>type</key>
                        <string>0</string>
                        <key>uuid</key>
                        <string>4</string>
                    </dict>
                </dict>
                <key>isViewVisible</key>
                <true/>
                <key>location</key>
                <string>309.000000:555.000000</string>
                <key>nibPath</key>
                <string>/System/Library/Automator/Run Shell Script.action/Contents/Resources/Base.lproj/main.nib</string>
            </dict>
            <key>isViewVisible</key>
            <true/>
        </dict>
    </array>
    <key>connectors</key>
    <dict>
        <key>A1B2C3D4-E5F6-7890-ABCD-EF1234567890</key>
        <dict>
            <key>from</key>
            <string>D6F6E1C8-1F5F-4C7F-0E3B-5D4E8F9A0B2C - D6F6E1C8-1F5F-4C7F-0E3B-5D4E8F9A0B2C</string>
            <key>to</key>
            <string>G9H0A1B2-3C4D-5E6F-7890-ABCDEF012345 - G9H0A1B2-3C4D-5E6F-7890-ABCDEF012345</string>
        </dict>
    </dict>
    <key>workflowMetaData</key>
    <dict>
        <key>applicationBundleID</key>
        <string>com.apple.Automator</string>
        <key>applicationBundleIDsByPath</key>
        <dict/>
        <key>applicationPath</key>
        <string>/System/Applications/Automator.app</string>
        <key>applicationPaths</key>
        <array>
            <string>/System/Applications/Automator.app</string>
        </array>
        <key>backgroundColor</key>
        <data>
        YnBsaXN0MDDUAQIDBAUGBwpYJHZlcnNpb25ZJGFyY2hpdmVyVCR0b3BYJG9iamVjdHMS
        AAGGoF8QD05TS2V5ZWRBcmNoaXZlctEICVRyb290gAGpCwwXGBkaGx4kVSRudWxs1Q0O
        DxAREhMUFRZWJGNsYXNzW05TQ29sb3JOYW1lXE5TQ29sb3JTcGFjZV1OU0NhdGFsb2dO
        YW1lV05TQ29sb3KACIADEAaAAoAEVlN5c3RlbV8QE3N5c3RlbUJhY2tncm91bmRDb2xv
        ctUNDg8QHyATIBYjgAiABRAMgAKAB1xzeXN0ZW1PcmFuZ2XSHB0eH1okY2xhc3NuYW1l
        WCRjbGFzc2VzV05TQ29sb3KiHiFYTlNPYmplY3TSGh0iI18QD05TS2V5ZWRBcmNoaXZl
        cqEjXxAPTlNLZXllZEFyY2hpdmVyAAgAEQAaACMALQAyADcAPwBFAEwAVABgAGUAcABz
        AHUAeACAAJEAlgCeAKAApQCqALwAwADNANIA4wDnAPQA+QAAAAAAAAIBAAAAAAAAACkA
        AAAAAAAAAAAAAAAAAAD7
        </data>
        <key>inputTypeIdentifier</key>
        <string>com.apple.Automator.fileSystemObject</string>
        <key>outputTypeIdentifier</key>
        <string>com.apple.Automator.nothing</string>
        <key>presentationMode</key>
        <integer>15</integer>
        <key>processesInput</key>
        <integer>0</integer>
        <key>serviceApplicationBundleID</key>
        <string></string>
        <key>serviceApplicationPath</key>
        <string></string>
        <key>serviceInputTypeIdentifier</key>
        <string>com.apple.Automator.fileSystemObject</string>
        <key>serviceOutputTypeIdentifier</key>
        <string>com.apple.Automator.nothing</string>
        <key>serviceProcessesInput</key>
        <integer>0</integer>
        <key>systemVersion</key>
        <array>
            <integer>14</integer>
            <integer>5</integer>
            <integer>0</integer>
        </array>
        <key>useAutomaticInputType</key>
        <integer>0</integer>
        <key>workflowTypeIdentifier</key>
        <string>com.apple.Automator.application</string>
    </dict>
</dict>
</plist>
EOF

echo "DreamBooth Droplet created on Desktop!"
echo "To use: Drag and drop your training images onto the droplet icon"