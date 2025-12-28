import { useEffect, useState, useMemo } from 'react'
import { searchCompany } from './action'

export function useCompanyInfo(searchKey) {
    const [companyInfo, setCompanyInfo] = useState([])
    const [originalCompanyInfo, setOriginalCompanyInfo] = useState([])
    useEffect(() => {
        const fetchCompanyInfo = async () => {
            try {
                const data = await searchCompany()
                setCompanyInfo(Array.isArray(data.stockList) ? data.stockList : [])
                setOriginalCompanyInfo(Array.isArray(data.stockList) ? data.stockList : [])
            } catch (e) {
                console.error(e)
                setCompanyInfo([])
                setOriginalCompanyInfo([])
            }
        }
        fetchCompanyInfo()
    }, [])

    const filterCompanyInfo = useMemo(() => {
        if (!searchKey) {
            // 只保留 Select options 需要的 value 和 label，避免多余属性传递到 DOM
            return originalCompanyInfo.slice(0, 10).map(item => ({
                value: item.code,
                label: item.zwjc,
            }))
        }
        
        const lowerKey = searchKey.toLowerCase().trim()
        if (!lowerKey) {
            return originalCompanyInfo.slice(0, 10).map(item => ({
                value: item.code,
                label: item.zwjc,
            }))
        }

        return originalCompanyInfo.filter(item => {
            const title = item.pinyin || ''
            const zwjc = item.zwjc || ''
            const code = item.code || ''
            return title.toLowerCase().includes(lowerKey) ||
                zwjc.toLowerCase().includes(lowerKey) ||
                code.toLowerCase().includes(lowerKey)
        }).slice(0, 10).map(item => ({
            value: item.code,
            label: item.zwjc,
        }))
    }, [originalCompanyInfo, searchKey])

    const filterCompanyCode2NameMap = useMemo(() => {
        return originalCompanyInfo.reduce((acc, item) => {
            acc[item.code] = item.zwjc
            return acc
        }, {})
    }, [originalCompanyInfo])

    return {filterCompanyInfo, filterCompanyCode2NameMap, originalCompanyInfo}
}