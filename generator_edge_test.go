package main

import "testing"

func TestGenerateHCLWithEdges(t *testing.T) {
    proj := Project{
        Nodes: []Node{{ID: "a", Type: "aws_instance", Attributes: map[string]string{"ami": "ami-123"}},
            {ID: "b", Type: "aws_security_group", Attributes: map[string]string{"name": "sg"}}},
        Edges: []Edge{{Source: "a", Target: "b", Type: "dependency"}},
    }
    hcl, err := GenerateHCL(proj)
    if err != nil {
        t.Fatalf("unexpected error: %v", err)
    }
    expected := "resource \"aws_instance\" \"a\" {\n  ami = \"ami-123\"\n}\n\nresource \"aws_security_group\" \"b\" {\n  name = \"sg\"\n  depends_on = [\"a\"]\n}\n\n"
    if hcl != expected {
        t.Fatalf("expected:\n%s\nGot:\n%s", expected, hcl)
    }
}
