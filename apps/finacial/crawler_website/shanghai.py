def shanghai_browser(page,searchWord):
    try:
        response = page.goto('https://www.sse.com.cn/disclosure/listedinfo/regular/')
        res = []
        if response is not None:
            print(f"页面加载状态码: {response.status}")
        
        # 等待页面加载
        page.wait_for_load_state('networkidle')
        page.wait_for_timeout(2000)  # 等待2秒，确保页面完全加载
        loading_locator = page.locator(".loading")
        # 等待 loading 元素隐藏（更可靠且 API 友好）
        # 使用 locator.wait_for(state='hidden') 可以直接等待元素变为隐藏状态，
        # 避免向 page.wait_for_function 传递 element handle 导致参数错误。
        try:
            loading_locator.wait_for(state="hidden", timeout=10000)
        except Exception:
            # 作为后备，使用全局 JS 表达式检测样式隐藏
            page.wait_for_function("() => document.querySelector('.loading')?.getAttribute('style') === 'display: none;'")

        
            # 等待 li 中 class=top_side_show_items 中 textcontent = 披露的元素出现
        search_input = page.wait_for_selector(".sse_searchInput > input")
        if search_input:
                # 清空并输入内容
            search_input.fill('')  # 清空搜索框
            search_input.fill(searchWord)  # delay参数模拟人工输入的速度
            
            # 方法1：使用 locator（推荐）
            search_button = page.locator('span.search_btn.bi-search')
            search_button.click()
            print("点击搜索按钮成功")
            
            # 等待搜索结果加载
            page.wait_for_load_state('networkidle')

            # 等待至少一个链接元素出现
            page.wait_for_timeout(2000)
            _ = page.wait_for_selector(".table-responsive")
            
            # 方法2：使用 locator().all()（推荐）
            print("\n方法2：使用 locator().all() 获取所有链接")
            all_links_locator = page.locator(".table-responsive a.table_titlewrap")
            all_links_count = all_links_locator.count()

            
            for i in range(all_links_count):
                link = all_links_locator.nth(i)
                text = link.inner_text()
                href = link.get_attribute('href')
                res.append({
                    'company_name': f"{searchWord}{text}",
                    'file_url': f"https://static.sse.com.cn{href}"
                })
                print(f"链接 {i + 1}: {text}")
                print(f"链接地址: {href}\n")
            return res

    except Exception as e:
        print(f"发生错误: {e}")
        return []