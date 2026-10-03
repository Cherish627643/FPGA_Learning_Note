# 基于ACG720开发板的FPGA设计流程——Verilog输入

## 一、课程目标与开发平台

本节课程以**二选一多路器（Mux2to1）**为例，演示基于高云 Gowin 软件进行 FPGA 开发与验证的完整流程。

- **开发板**：ACG720 或 ACG750（二者硬件资源相同，仅封装引脚不同）
- **FPGA 芯片型号**：`GW5AT-LV138PG484AC1/I0`
  - 另有 60K 版本：`GW5AT-LV60PG484AC1/I0`
  - 通过芯片丝印判断版本号（型号下一行的字母，如 `2404B` 中的 `B` 即为版本号）
- **开发软件**：Gowin，版本 `1.9.12`（目前最新，后续更新版本使用方式类似）

---

## 二、创建工程

### 2.1 打开 Gowin 软件

双击桌面 Gowin 1.9.12 图标启动软件。启动后界面分为四栏：

| 栏位 | 含义 |
|---|---|
| Recent Project | 近期打开过的工程 |
| Quick Start | 快速开始（New Project / Open Project / Open Example Project） |
| Tools | 工具集合（Flow Planner 物理约束、Timing Constraints Editor 时序约束、Programmer 下载等） |
| User Manuals | 用户手册链接到高云官网 |

原厂示例工程（Example Project）配置不错但价格昂贵，适合有经验的工程师评估使用；新手短期用不上，关闭即可。

### 2.2 新建工程步骤

1. 点击 **New Project** → 弹出对话框 → 选择 **FPGA Design Project** → OK
2. 进入 **Project Name** 页：
   - 工程名 `Name`：输入 `mux2to1`（命名要有实际意义）
   - 路径 `Create in`：选择工程存放目录
   - 勾选 `Used as default project location`（下次建工程默认此路径，可按需选择）

> **注意事项**：
> - 工程名不能含中文和空格，否则流程会报错
> - 路径不能过长：Windows 限制 260 字符，Linux 限制 4096 字符

3. 进入 **Select Device** 页（关键步骤）：
   - Device：选择芯片具体型号
   - 选 `GW5AT-LV138PG484AC1/I0`，Version 选 `B`
   - 若使用 60K 版本，则改为 `GW5AT-LV60PG484AC1/I0`
4. 进入 **Summary** 页：核对所有设置，点击 **Finish** 完成工程创建。

---

## 三、Verilog 设计输入

### 3.1 新建 Verilog 源文件

1. 菜单栏 **File → New**（或快捷键 `Ctrl + N`）
2. 在弹出的选项卡中选择 **Verilog File**（在 Files 分类下）
3. 命名：与工程名保持一致，输入 `mux2to1` → OK

> 其他类型的文件（如 VHDL、约束文件等）目前用不到，无需关注。

### 3.2 Verilog 代码结构

任意 Verilog 模块都以 `module` 关键字开始，以 `endmodule` 结束。模块名紧跟 `module` 之后。

```verilog
module mux2to1(
    // 端口列表
    a,        // 输入
    b,        // 输入
    sel,      // 选择端
    out       // 输出
);
    // 端口类型声明
    input  a;
    input  b;
    input  sel;
    output out;

    // 逻辑功能描述
    assign out = (sel == 0) ? a : b;

endmodule
```

### 3.3 端口列表与端口声明

- 端口列表写在 `module 模块名(...)` 后的括号中，以 **逗号** 分隔，最后一个端口后 **无逗号**
- 括号结束必须紧跟 **分号 `;`**
- 输入信号用 `input` 声明，输出信号用 `output` 声明
- 每个端口声明后用 **分号 `;`** 结尾（不再是逗号）

### 3.4 Verilog 语法细节

- **大小写敏感**：大写 `A` 与小写 `a` 是两个不同信号
- **字符必须为英文**：所有标点（逗号、分号、括号、冒号、问号）都不能使用中文符号
- **连续赋值语句**：使用 `assign` 关键字，对 wire 类型信号赋值
  - 等号左边 `out`：表示被赋值的对象（输出端口）
  - 等号右边表达式：根据条件决定 `out` 的值

### 3.5 二选一多路器功能描述

二选一多路器的逻辑关系：

| sel 取值 | out 输出 |
|---|---|
| 0 | a |
| 1 | b |

使用**三元运算符**一行实现：

```verilog
assign out = (sel == 0) ? a : b;
```

语法解释：判断 `sel == 0` 是否成立，若成立则 `out = a`，否则 `out = b`。这是一种互斥关系。

---

## 四、语法检查与综合

### 4.1 语法检查

按 `Ctrl + S` 保存文件后，切换到 **Hierarchy（层次结构）** 界面：
- 若代码有语法错误，会在窗口顶部以 **红色字体** 显示 `RTL Analysis Error`，并指出错误所在行
- 故意将英文分号 `;` 改为中文分号 `；` 后保存，会触发该错误提示；改回英文分号后错误消失

### 4.2 综合（Synthesis）

在 **Process** 界面，双击 **Synthesize** 按钮，Gowin 软件会对代码进行分析与综合。

### 4.3 查看 RTL 视图

综合完成后：
1. 点击 **Tools → Schematic Viewer → RTL Design View**
2. 即可看到电路模型图

> **观察要点**：
> - 电路图与之前绘制的二选一多路器符号图基本一致
> - `sel` 信号后面会自动接一个 **非门（取反）**
> - 当 `sel == 0` 时，经非门变为 `1`，输出 `a` 的值
> - 当 `sel == 1` 时，经非门变为 `0`，输出 `b` 的值
> - 综合后的电路与功能预期一致

---

## 五、本节课程总结

通过本节课程，完成了以下环节：

1. **创建工程**：基于 ACG720 / ACG750 开发板，选择对应的芯片型号
2. **设计输入**：以 HDL（Verilog）方式编写二选一多路器代码
3. **语法检查**：通过 Hierarchy 界面查看语法错误
4. **综合与 RTL 查看**：使用 Synthesize 得到电路模型图

设计验证（仿真验证）环节将放到下一节课讲解。建议课后将本节流程重复操作 2~3 遍，在实践中理解每个环节的作用。