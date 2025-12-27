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
        if (!searchKey) return companyInfo
        const lowerKey = searchKey.toLowerCase().trim()
        if (!lowerKey) return companyInfo

        return companyInfo.filter(item => {
            const title = item.pinyin || item.zwjc || ''
            const code = item.code
            return title.toLowerCase().includes(lowerKey) ||
                code.toLowerCase().includes(lowerKey)
        }).map(item => ({
            value: item.code,
            label: item.zwjc,
            ...item
        })).slice(0, 10)
    }, [companyInfo, searchKey])

    return filterCompanyInfo
}