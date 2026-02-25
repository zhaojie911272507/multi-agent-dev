from IPython.display import Image, display

def draw_graph_img(graph,*,rename=False):
    try:
        # display(Image(graph.get_graph().draw_mermaid_png()))
        # 获取 PNG 数据
        png_data = graph.get_graph().draw_mermaid_png()
        if rename:
            filename = f"{rename}.png"
        else:
            filename = f"{graph}.png"
        # 保存到本地
        with open(filename, "wb") as f:
            f.write(png_data)

        # 显示图像（确保路径正确）
        display(Image(filename=filename))

    except Exception:
        # This requires some extra dependencies and is optional
        pass

