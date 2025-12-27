'use server' // 必须在文件顶部标记
export async function searchCompany(query) {
    // 这里可以安全地写后端代码（查数据库、调第三方API等）
    console.log('Server side searching:', query);

    // 模拟请求
    const res = await fetch(`http://127.0.0.1:8000/get_company_info`);
    const data = await res.json();

    return data;
}
