import { Suggestion } from '@ant-design/x';
import { useState } from 'react';


export default function SenderHeader(props) {

    const { companyInfo = [], children } = props
//    const [suggestions, setSuggestions] = useState([])

    return (
        <Suggestion
            items={companyInfo}>
            { 
                ({ onTrigger, onKeyDown, open }) => { 
                    return <>{ children }</> 
                }
            }
        </Suggestion>
    )
}