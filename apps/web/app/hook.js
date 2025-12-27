import { useEffect, useState, useMemo } from 'react'
import { searchCompany } from './action'

export function useCompanyInfo(searchKey) {
    const [companyInfo, setCompanyInfo] = useState([])
    useEffect(() => {
        const fetchCompanyInfo = async () => {
            try {
                const data = await searchCompany()
                setCompanyInfo(Array.isArray(data.stockList) ? data.stockList : [])
            } catch (e) {
                console.error(e)
                setCompanyInfo([])
            }
        }
        fetchCompanyInfo()
    }, [])

    const filterCompanyInfo = useMemo(() => {
        // 先转换为 Suggestion 需要的格式（必须有 value 和 label）
        const formattedList = companyInfo.map(item => ({
            value: item.code,
            label: item.zwjc,
            ...item
        }))

        if (!searchKey) return formattedList.slice(0, 10)
        
        const lowerKey = searchKey.toLowerCase().trim()
        if (!lowerKey) return formattedList.slice(0, 10)

        return formattedList.filter(item => {
            const title = item.pinyin || item.zwjc || ''
            const code = item.code || ''
            return title.toLowerCase().includes(lowerKey) ||
                code.toLowerCase().includes(lowerKey)
        }).slice(0, 10)
    }, [companyInfo, searchKey])

    const filterCompanyCode2NameMap = useMemo(() => {
        return companyInfo.reduce((acc, item) => {
            acc[item.code] = item.zwjc
            return acc
        }, {})
    }, [companyInfo])

    return {filterCompanyInfo, filterCompanyCode2NameMap}
}