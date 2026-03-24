import unittest
import json
from generate_hcl import generate_hcl

class TestGenerateHCL(unittest.TestCase):
    def test_simple(self):
        proj = {
            "nodes": [
                {
                    "id": "my_instance",
                    "type": "aws_instance",
                    "attributes": {"ami": "ami-12345", "instance_type": "t2.micro"}
                }
            ],
            "edges": []
        }
        expected = (
            'resource "aws_instance" "my_instance" {\n'
            '  ami = "ami-12345"\n'
            '  instance_type = "t2.micro"\n'
            '}\n\n'
        )
        self.assertEqual(generate_hcl(proj), expected)

if __name__ == '__main__':
    unittest.main()
