const SH_CODE = {
    600: "SH",
    601: "SH",
    603: "SH",
    688: "SH",
    900: "SH",
}

const SZ_CODE = {
    '000': "SZ",
    '002': "SZ",
    '300': "SZ",
    '301': "SZ",
    200: "SZ",
}

const BJ_CODE = {
    920: "BJ",
    83: "BJ",
    87: "BJ",
    43: "BJ",
    804: "BJ",
}

export const EXCHANGE_CODE_MAP = {
    "gfbj": "BJ",
    "gssz": "SZ",
    "gssh": "SH",
    ...SH_CODE,
    ...SZ_CODE,
    ...BJ_CODE,
}

