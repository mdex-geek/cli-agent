import unittest
from unittest.mock import patch
from pieces.assets import AssetsCommands,AssetsCommandsApi
from pieces.settings import Settings
import sys
from io import StringIO
import random,os
import json
from pieces.utils import sanitize_filename

class TestOpenSaveCommand(unittest.TestCase):
    def test_open_command(self,ITEM_INDEX=None):
        Settings.startup()
        stdout = sys.stdout
        sys.stdout = StringIO()


        assets_length = len(AssetsCommandsApi().assets_snapshot)


        sys.stdout = StringIO()
        if not ITEM_INDEX:
            ITEM_INDEX = random.randint(1,assets_length)

        # Act
        AssetsCommands.open_asset(ITEM_INDEX = ITEM_INDEX)

        result_open = sys.stdout.getvalue()
        
        sys.stdout = stdout  # Reset sys.stdout to its original state

        result_list = result_open.strip().split('\n')

        name = result_list[-6].removeprefix('Name: ')
        created_readable = result_list[-5].removeprefix('Created: ')
        updated_readable = result_list[-4].removeprefix('Updated: ')
        type = result_list[-3].removeprefix('Type: ')
        language = result_list[-2].removeprefix('Language: ')
        code_snippet_path = result_list[-1].removeprefix('Code: ')


        with open(Settings.extensions_dir) as f:
            language_extension_mapping = json.load(f)
        self.assertTrue(os.path.exists(code_snippet_path))  # assert that the code snippet file exists
        self.assertEqual(os.path.splitext(code_snippet_path)[-1], language_extension_mapping[language])  # assert that the file extension matches the language
        self.assertEqual(os.path.splitext(os.path.basename(code_snippet_path))[0], sanitize_filename(name))

        return code_snippet_path # Return the code path to be tested for the save command
        
    @patch('builtins.input', side_effect=['y','y'])
    @patch('pyperclip.paste', return_value='print("Hello, World!")')
    def test_save_command(self, mock_paste,mock_buildins):
        Settings.startup()
        TEXT = "TEST SNIPPET CODE"
        # Call create_asset to create a new asset to test on
        AssetsCommands.create_asset() # Create a hello world asset

        AssetsCommandsApi().assets_snapshot = {AssetsCommands.current_asset:None} # Update the asset cache

        code_snippet_path = self.test_open_command(ITEM_INDEX=1) # Open the created asset

        with open(code_snippet_path,'w') as f:
            f.write(TEXT)

        AssetsCommands.update_asset() # Run the save


        code = AssetsCommandsApi.update_asset_snapshot(AssetsCommands.current_asset).formats.iterable[0].fragment.string.raw

        self.assertEqual(code, TEXT) # Check if the code was saved

        AssetsCommands.delete_asset() # Delete the asset
        


if __name__ == '__main__':
    unittest.main()

