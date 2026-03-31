import unittest
from unittest.mock import patch
import runpy

class TestExe(unittest.TestCase):
    @patch('subprocess.Popen')
    def test_exe_runs_streamlit(self, mock_popen):
        runpy.run_path('exe.py', run_name='__main__')
        mock_popen.assert_called_once_with('streamlit run page.py', shell=True)

if __name__ == '__main__':
    unittest.main()
