import time
import pandas as pd
from playwright.sync_api import sync_playwright
import os

def run():
    # 1. 准备工作
    screenshot_dir = "debug_screenshots"
    if not os.path.exists(screenshot_dir):
        os.makedirs(screenshot_dir)

    output_file = "guangdong_cosmetics_v2.csv"
    if not os.path.exists(output_file):
        df = pd.DataFrame(columns=["产品名称", "企业名称", "注册证号", "批件状态", "产品执行标准全文"])
        df.to_csv(output_file, index=False, encoding='utf-8-sig')

    print("启动浏览器...")
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False, slow_mo=1000, args=['--start-maximized'])

        context = browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
            viewport={"width": 1920, "height": 1080},
            ignore_https_errors=True
        )

        page = context.new_page()

        url = "https://www.nmpa.gov.cn/datasearch/home-index.html?itemId=ff8080818046502f0180f934f6873f78#category=hzp"
        print(f"打开网址: {url}")

        try:
            page.goto(url, timeout=60000, wait_until="domcontentloaded")
            page.wait_for_load_state("networkidle", timeout=10000)
        except Exception as e:
            print(f"页面加载警告: {e}")

        # --- 筛选广东省 ---
        print("准备筛选 '广东省'...")
        time.sleep(5)

        try:
            gd_btn = page.locator("a:has-text('广东'), span:has-text('广东'), div:has-text('广东')").first
            if gd_btn.count() == 0:
                print("未自动找到'广东'按钮，请手动点击！")
                page.screenshot(path=f"{screenshot_dir}/before_filter.png")
            else:
                print("点击 '广东'...")
                # 用户反馈点击筛选可能打开新标签页，捕捉新页面
                try:
                    with context.expect_page(timeout=5000) as new_page_info:
                        gd_btn.click()

                    new_page = new_page_info.value
                    new_page.wait_for_load_state("domcontentloaded")
                    print("检测到新标签页打开，切换上下文...")
                    page = new_page
                    page.bring_to_front()
                except Exception:
                    # 如果 expect_page 超时(即没有新页面打开)，说明在原页面刷新
                    print("未检测到新标签页，继续在当前页面等待刷新...")
                    time.sleep(5)

        except Exception as e:
            print(f"筛选操作异常: {e}")
            time.sleep(5)

        page.screenshot(path=f"{screenshot_dir}/after_filter.png")

        # --- 开始循环处理 ---
        page_num = 1

        while True:
            print(f"\n>>> 正在处理第 {page_num} 页 <<<")

            try:
                page.wait_for_selector("tr", timeout=10000)
            except:
                print("等待表格超时。")

            # 获取所有行
            rows = page.locator("tr").all()

            # 过滤出有效的数据行 (带详情按钮的)
            data_rows = []
            for r in rows:
                if r.locator("text=详情").count() > 0:
                    data_rows.append(r)

            print(f"本页发现 {len(data_rows)} 条数据行。")

            if len(data_rows) == 0:
                print("未发现数据行，可能是网络延迟或已无数据。")
                page.screenshot(path=f"{screenshot_dir}/no_data_page_{page_num}.png")
                time.sleep(5)
                # Retry
                rows = page.locator("tr").all()
                data_rows = [r for r in rows if r.locator("text=详情").count() > 0]
                if len(data_rows) == 0:
                    break

            for i in range(len(data_rows)):
                try:
                    # 重新定位
                    current_rows = page.locator("tr:has-text('详情')").all()
                    if i >= len(current_rows):
                        break

                    row = current_rows[i]

                    # --- 1. 在列表页提取基础信息 ---
                    cells = row.locator("td").all()

                    # 默认值
                    p_name = "未获取"
                    ent_name = "未获取"
                    reg_no = "未获取"
                    status = "未获取"

                    if len(cells) >= 5:
                        # 根据之前的经验/假设
                        # 0: 序号, 1: 产品名称, 2: 注册人, 3: 注册证号, 4: 状态, 5: 详情
                        p_name = cells[1].inner_text().strip()
                        ent_name = cells[2].inner_text().strip()
                        reg_no = cells[3].inner_text().strip()
                        status = cells[4].inner_text().strip()
                    else:
                        # Fallback: 尝试直接获取文本
                        full_text = row.inner_text()
                        print(f"  行结构异常: {full_text[:30]}...")
                        # 仍尝试继续，看状态是否在文本中
                        status = full_text

                    # --- 2. 过滤非当前批件 ---
                    if "当前批件" not in status:
                        print(f"  跳过: {p_name} ({status}) - 非当前批件")
                        continue

                    print(f"  处理: {p_name} | {status}")

                    # --- 3. 进入详情页获取PDF ---
                    detail_btn = row.locator("text=详情").first

                    formula_text = "无查看按钮"

                    with context.expect_page(timeout=30000) as detail_page_info:
                        detail_btn.click()

                    detail_page = detail_page_info.value
                    detail_page.wait_for_load_state("domcontentloaded")

                    # 用户提示详情页有约3秒加载时间，增加等待逻辑
                    print("    进入详情页，等待数据加载...")
                    try:
                        # 显式等待包含目标文本的行出现
                        detail_page.wait_for_selector("tr:has-text('产品执行的标准'), tr:has-text('技术要求')", timeout=10000)
                    except:
                        print("    等待标准行超时，尝试直接查找...")

                    time.sleep(2) # 额外缓冲

                    try:
                        # 寻找“产品执行的标准”或“技术要求”所在的行
                        std_row = detail_page.locator("tr").filter(has_text="产品执行的标准").or_(detail_page.locator("tr").filter(has_text="技术要求")).first

                        if std_row.count() > 0:
                            # 查找该行内的“查看”按钮 (可能是 span, a, 或 button)
                            view_btn = std_row.locator("text=查看").first

                            if view_btn.count() > 0 and view_btn.is_visible():
                                print("    点击查看标准...")

                                with context.expect_page(timeout=20000) as pdf_page_info:
                                    view_btn.click()

                                pdf_page = pdf_page_info.value
                                pdf_page.wait_for_load_state("domcontentloaded")
                                time.sleep(3) # 等待PDF查看器或内容加载

                                pdf_url = pdf_page.url
                                print(f"    PDF/内容页链接: {pdf_url}")

                                formula_text = pdf_url
                                if "url=" in pdf_url:
                                    try:
                                        import urllib.parse
                                        raw_url = pdf_url.split("url=")[1].split("&")[0]
                                        decoded_url = urllib.parse.unquote(raw_url)
                                        formula_text = f"{decoded_url}"
                                    except:
                                        pass

                                pdf_page.close()
                            else:
                                print("    该行未找到可见的'查看'按钮")
                        else:
                            print("    页面中未找到'产品执行的标准'或'技术要求'行")
                            # 截图以供调试
                            detail_page.screenshot(path=f"{screenshot_dir}/detail_missing_std_{int(time.time())}.png")

                    except Exception as e:
                        print(f"    提取标准失败: {e}")
                        formula_text = f"提取错误: {e}"

                    # 保存数据
                    new_row = {
                        "产品名称": p_name,
                        "企业名称": ent_name,
                        "注册证号": reg_no,
                        "批件状态": status,
                        "产品执行标准全文": formula_text
                    }

                    df = pd.DataFrame([new_row])
                    df.to_csv(output_file, mode='a', header=False, index=False, encoding='utf-8-sig')

                    detail_page.close()

                except Exception as e:
                    print(f"行处理错误: {e}")
                    try:
                        if 'detail_page' in locals() and not detail_page.is_closed():
                            detail_page.close()
                    except:
                        pass

            # 翻页
            print("尝试翻页...")
            try:
                # 增加对 Element UI 右箭头按钮的支持 (class="btn-next" 或包含 el-icon-arrow-right 的按钮)
                next_btn = page.locator("button.btn-next, a:has-text('下一页'), li.next, button:has(i.el-icon-arrow-right)").first

                if next_btn.count() > 0:
                    if next_btn.get_attribute("disabled") or "disabled" in next_btn.get_attribute("class"):
                        print("已是最后一页。")
                        break

                    next_btn.click()
                    time.sleep(5)
                else:
                    current_page_num_el = page.locator("ul.el-pager li.active").first
                    if current_page_num_el.count() > 0:
                        curr_num = int(current_page_num_el.inner_text())
                        next_num_el = page.locator(f"ul.el-pager li:has-text('{curr_num + 1}')").first
                        if next_num_el.count() > 0:
                            next_num_el.click()
                            time.sleep(5)
                            page_num += 1
                        else:
                            print("未找到下一页页码，结束。")
                            break
                    else:
                        print("未找到翻页控件，结束。")
                        break
            except Exception as e:
                print(f"翻页异常: {e}")
                break

        print(f"任务完成。文件已保存至 {output_file}")
        browser.close()

if __name__ == "__main__":
    run()
