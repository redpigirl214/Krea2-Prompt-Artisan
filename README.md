# Krea2 Prompt Artisan

本技能适用于 Codex，用来生成 Krea 2 模型适用的提示词。

它可以把一句中文想法、已有提示词，或者一张参考图，整理成更适合 Krea 2 模型使用的高密度英文提示词，并同时生成中文译文和一个带复制按钮的本地 HTML 页面。

## 适合做什么

- 生成 Krea 2 模型使用的图片提示词
- 把普通中文想法扩写成英文长提示词
- 把已有提示词改写成 Krea 2 风格，比如把动漫模型 anima 的提示词改成 Krea 2 适用的提示词
- 上传你的图片，生成该图片的 Krea 2 提示词
- 生成带中文译文、拆解说明和复制按钮的 HTML 成品页

## 下载安装

下载页面右侧 Release 里的压缩包：

```text
krea2-prompt-artisan-v1.0.0.zip
```

解压后应得到这个文件夹：

```text
krea2-prompt-artisan
```

把整个文件夹放到 Codex 的 skills 目录下：

```text
%USERPROFILE%\.codex\skills\
```

最终目录应类似：

```text
%USERPROFILE%\.codex\skills\krea2-prompt-artisan\SKILL.md
```

放好后，重启 Codex 或重新打开一个会话。

## 怎么使用

重启后，在 Codex 里用自然语言触发即可，例如：

```text
生成K2提示词：一个美女撑着透明雨伞，在雨中侧身看向路旁
```

```text
生成附图的K2提示词
```

```text
把下面的提示词转成K2提示词：雨夜街头，一个穿黑色风衣的女人站在霓虹灯下
```

```text
K2化这个画面：森林里的白色小屋，窗户亮着暖光，门前有积雪
```

```text
生成一段k2提示词：赛博朋克城市天台，少女回头，远处有飞行器
```

## 输出结果

技能会默认生成一个本地 HTML 文件，里面通常包含：

- 英文 Krea 2 提示词
- 中文译文
- 八项提示词拆解说明
- 优化说明
- 一行七言短诗
- 复制按钮

默认输出目录通常是codex当前工作目录下的：

```text
Krea2提示词
```

## 注意事项

- 这个技能负责生成提示词，不负责直接生成图片。
- 如果使用附图，请把图片发给当前对话，让 Codex 能看到它。
- HTML 渲染脚本只使用 Python 标准库，一般不需要额外安装依赖。
- 如果浏览器没有自动打开，可以根据对话里返回的 HTML 路径手动打开。

## 文件结构

```text
krea2-prompt-artisan
├─ SKILL.md
├─ assets
│  └─ html_template.html
├─ references
│  └─ krea2_system_prompt.md
└─ scripts
   └─ render_krea2_html.py
```
