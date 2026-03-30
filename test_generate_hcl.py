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

    def test_with_edges(self):
        proj = {
            "nodes": [
                {"id": "a", "type": "aws_instance", "attributes": {"ami": "ami-123"}},
                {"id": "b", "type": "aws_security_group", "attributes": {"name": "sg"}}
            ],
            "edges": [
                {"source": "a", "target": "b", "type": "dependency"}
            ]
        }
        expected = (
            'resource "aws_instance" "a" {\n'
            '  ami = "ami-123"\n'
            '}\n\n'
            'resource "aws_security_group" "b" {\n'
            '  name = "sg"\n'
            '  depends_on = ["a"]\n'
            '}\n\n'
        )
        self.assertEqual(generate_hcl(proj), expected)

if __name__ == '__main__':
    unittest.main()
