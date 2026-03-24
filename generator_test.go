package main

import "testing"

func TestGenerateHCL(t *testing.T) {
    proj := Project{
        Nodes: []Node{{ID: "my_instance", Type: "aws_instance", Attributes: map[string]string{"ami": "ami-12345", "instance_type": "t2.micro"}}},
        Edges: []Edge{},
    }
    hcl, err := GenerateHCL(proj)
    if err != nil {
        t.Fatalf("unexpected error: %v", err)
    }
    expected := "resource \"aws_instance\" \"my_instance\" {\n  ami = \"ami-12345\"\n  instance_type = \"t2.micro\"\n}\n\n"
    if hcl != expected {
        t.Fatalf("expected:\n%s\nGot:\n%s", expected, hcl)
    }
}
