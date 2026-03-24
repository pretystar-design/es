# 图形化 Terraform 代码生成工具

本项目实现了一个最小原型，用于将 **JSON 形式的可视化模型** 转换为 **Terraform HCL**，并附带单元测试。它对应于 `user_stories.md` 中的核心需求（资源编辑、属性配置、实时 HCL 预览、代码导出等），为后续 UI、验证、插件等功能提供基础。

## 目录结构

- `generate_hcl.py` – 核心 HCL 生成器（Python）
- `test_generate_hcl.py` – 对生成器的单元测试
- `model.go`, `generator.go`, `main.go` – 预备的 Go 代码骨架（可在后续迁移到 Go 实现）
- `user_stories.md` – 需求文档
- `README.md` – 本说明
- `example_model.json` – 示例模型文件，演示如何使用生成器

## 使用方法

```bash
# 生成 HCL
python3 generate_hcl.py example_model.json > output.tf

# 运行测试
python3 -m unittest discover -v
```

## 示例模型 (`example_model.json`)
```json
{
  "nodes": [
    {
      "id": "my_instance",
      "type": "aws_instance",
      "attributes": {
        "ami": "ami-12345",
        "instance_type": "t2.micro"
      }
    }
  ],
  "edges": []
}
```

## 下一步计划（对应 user_stories）
1. **UI** – 使用 React‑Flow 或类似库实现可视化画布。
2. **实时 HCL 预览** – 前端调用 `generate_hcl.py`（或改写为 Go/Node）并显示结果。
3. **Terraform 验证** – 集成 HashiCorp Terraform SDK 执行 `validate`/`plan`。
4. **导入 tfstate** – 解析已有状态并生成对应节点。
5. **插件系统** – 定义插件 API，让自研 Provider 可以注册 UI 组件。
6. **CI 集成** – 提供 CLI / REST 接口供 CI 流水线调用。

---

*此项目为原型，欢迎根据实际需求继续扩展。*