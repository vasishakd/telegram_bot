from enum import StrEnum


class SubscriptionType(StrEnum):
    anime = 'ANIME'
    manga = 'MANGA'


class Currency(StrEnum):
    AED = 'AED'
    AFN = 'AFN'
    ALL = 'ALL'
    AMD = 'AMD'
    ANG = 'ANG'
    AOA = 'AOA'
    ARS = 'ARS'
    AUD = 'AUD'
    AWG = 'AWG'
    AZN = 'AZN'
    BAM = 'BAM'
    BBD = 'BBD'
    BDT = 'BDT'
    BGN = 'BGN'
    BHD = 'BHD'
    BIF = 'BIF'
    BMD = 'BMD'
    BND = 'BND'
    BOB = 'BOB'
    BRL = 'BRL'
    BSD = 'BSD'
    BTN = 'BTN'
    BWP = 'BWP'
    BYN = 'BYN'
    BZD = 'BZD'
    CAD = 'CAD'
    CDF = 'CDF'
    CHF = 'CHF'
    CLP = 'CLP'
    CNY = 'CNY'
    COP = 'COP'
    CRC = 'CRC'
    CUP = 'CUP'
    CVE = 'CVE'
    CZK = 'CZK'
    DJF = 'DJF'
    DKK = 'DKK'
    DOP = 'DOP'
    DZD = 'DZD'
    EGP = 'EGP'
    ERN = 'ERN'
    ETB = 'ETB'
    EUR = 'EUR'
    FJD = 'FJD'
    FKP = 'FKP'
    GBP = 'GBP'
    GEL = 'GEL'
    GGP = 'GGP'
    GHS = 'GHS'
    GIP = 'GIP'
    GMD = 'GMD'
    GNF = 'GNF'
    GTQ = 'GTQ'
    GYD = 'GYD'
    HKD = 'HKD'
    HNL = 'HNL'
    HRK = 'HRK'
    HTG = 'HTG'
    HUF = 'HUF'
    IDR = 'IDR'
    ILS = 'ILS'
    IMP = 'IMP'
    INR = 'INR'
    IQD = 'IQD'
    IRR = 'IRR'
    ISK = 'ISK'
    JEP = 'JEP'
    JMD = 'JMD'
    JOD = 'JOD'
    JPY = 'JPY'
    KES = 'KES'
    KGS = 'KGS'
    KHR = 'KHR'
    KID = 'KID'
    KMF = 'KMF'
    KRW = 'KRW'
    KWD = 'KWD'
    KYD = 'KYD'
    KZT = 'KZT'
    LAK = 'LAK'
    LBP = 'LBP'
    LKR = 'LKR'
    LRD = 'LRD'
    LSL = 'LSL'
    LYD = 'LYD'
    MAD = 'MAD'
    MDL = 'MDL'
    MGA = 'MGA'
    MKD = 'MKD'
    MMK = 'MMK'
    MNT = 'MNT'
    MOP = 'MOP'
    MRU = 'MRU'
    MUR = 'MUR'
    MVR = 'MVR'
    MWK = 'MWK'
    MXN = 'MXN'
    MYR = 'MYR'
    MZN = 'MZN'
    NAD = 'NAD'
    NGN = 'NGN'
    NIO = 'NIO'
    NOK = 'NOK'
    NPR = 'NPR'
    NZD = 'NZD'
    OMR = 'OMR'
    PAB = 'PAB'
    PEN = 'PEN'
    PGK = 'PGK'
    PHP = 'PHP'
    PKR = 'PKR'
    PLN = 'PLN'
    PYG = 'PYG'
    QAR = 'QAR'
    RON = 'RON'
    RSD = 'RSD'
    RUB = 'RUB'
    RWF = 'RWF'
    SAR = 'SAR'
    SBD = 'SBD'
    SCR = 'SCR'
    SDG = 'SDG'
    SEK = 'SEK'
    SGD = 'SGD'
    SHP = 'SHP'
    SLE = 'SLE'
    SOS = 'SOS'
    SRD = 'SRD'
    SSP = 'SSP'
    STN = 'STN'
    SYP = 'SYP'
    SZL = 'SZL'
    THB = 'THB'
    TJS = 'TJS'
    TMT = 'TMT'
    TND = 'TND'
    TOP = 'TOP'
    TRY = 'TRY'
    TTD = 'TTD'
    TVD = 'TVD'
    TWD = 'TWD'
    TZS = 'TZS'
    UAH = 'UAH'
    UGX = 'UGX'
    USD = 'USD'
    UYU = 'UYU'
    UZS = 'UZS'
    VES = 'VES'
    VND = 'VND'
    VUV = 'VUV'
    WST = 'WST'
    XAF = 'XAF'
    XCD = 'XCD'
    XDR = 'XDR'
    XOF = 'XOF'
    XPF = 'XPF'
    YER = 'YER'
    ZAR = 'ZAR'
    ZMW = 'ZMW'
    ZWL = 'ZWL'

    @property
    def full_name(self) -> str:
        return {
            self.AED: 'United Arab Emirates dirham',
            self.AFN: 'Afghan afghani',
            self.ALL: 'Albanian lek',
            self.AMD: 'Armenian dram',
            self.ANG: 'Netherlands Antillean guilder',
            self.AOA: 'Angolan kwanza',
            self.ARS: 'Argentine peso',
            self.AUD: 'Australian dollar',
            self.AWG: 'Aruban florin',
            self.AZN: 'Azerbaijani manat',
            self.BAM: 'Bosnia and Herzegovina convertible mark',
            self.BBD: 'Barbados dollar',
            self.BDT: 'Bangladeshi taka',
            self.BGN: 'Bulgarian lev',
            self.BHD: 'Bahraini dinar',
            self.BIF: 'Burundian franc',
            self.BMD: 'Bermudian dollar',
            self.BND: 'Brunei dollar',
            self.BOB: 'Boliviano',
            self.BRL: 'Brazilian real',
            self.BSD: 'Bahamian dollar',
            self.BTN: 'Bhutanese ngultrum',
            self.BWP: 'Botswana pula',
            self.BYN: 'Belarusian ruble',
            self.BZD: 'Belize dollar',
            self.CAD: 'Canadian dollar',
            self.CDF: 'Congolese franc',
            self.CHF: 'Swiss franc',
            self.CLP: 'Chilean peso',
            self.CNY: 'Chinese yuan',
            self.COP: 'Colombian peso',
            self.CRC: 'Costa Rican colón',
            self.CUP: 'Cuban peso',
            self.CVE: 'Cape Verdean escudo',
            self.CZK: 'Czech koruna',
            self.DJF: 'Djiboutian franc',
            self.DKK: 'Danish krone',
            self.DOP: 'Dominican peso',
            self.DZD: 'Algerian dinar',
            self.EGP: 'Egyptian pound',
            self.ERN: 'Eritrean nakfa',
            self.ETB: 'Ethiopian birr',
            self.EUR: 'Euro',
            self.FJD: 'Fijian dollar',
            self.FKP: 'Falkland Islands pound',
            self.GBP: 'Pound sterling',
            self.GEL: 'Georgian lari',
            self.GGP: 'Guernsey pound',
            self.GHS: 'Ghanaian cedi',
            self.GIP: 'Gibraltar pound',
            self.GMD: 'Gambian dalasi',
            self.GNF: 'Guinean franc',
            self.GTQ: 'Guatemalan quetzal',
            self.GYD: 'Guyanese dollar',
            self.HKD: 'Hong Kong dollar',
            self.HNL: 'Honduran lempira',
            self.HRK: 'Croatian kuna',
            self.HTG: 'Haitian gourde',
            self.HUF: 'Hungarian forint',
            self.IDR: 'Indonesian rupiah',
            self.ILS: 'Israeli new shekel',
            self.IMP: 'Isle of Man pound',
            self.INR: 'Indian rupee',
            self.IQD: 'Iraqi dinar',
            self.IRR: 'Iranian rial',
            self.ISK: 'Icelandic króna',
            self.JEP: 'Jersey pound',
            self.JMD: 'Jamaican dollar',
            self.JOD: 'Jordanian dinar',
            self.JPY: 'Japanese yen',
            self.KES: 'Kenyan shilling',
            self.KGS: 'Kyrgyzstani som',
            self.KHR: 'Cambodian riel',
            self.KID: 'Kiribati dollar',
            self.KMF: 'Comorian franc',
            self.KRW: 'South Korean won',
            self.KWD: 'Kuwaiti dinar',
            self.KYD: 'Cayman Islands dollar',
            self.KZT: 'Kazakhstani tenge',
            self.LAK: 'Lao kip',
            self.LBP: 'Lebanese pound',
            self.LKR: 'Sri Lankan rupee',
            self.LRD: 'Liberian dollar',
            self.LSL: 'Lesotho loti',
            self.LYD: 'Libyan dinar',
            self.MAD: 'Moroccan dirham',
            self.MDL: 'Moldovan leu',
            self.MGA: 'Malagasy ariary',
            self.MKD: 'Macedonian denar',
            self.MMK: 'Burmese kyat',
            self.MNT: 'Mongolian tögrög',
            self.MOP: 'Macanese pataca',
            self.MRU: 'Mauritanian ouguiya',
            self.MUR: 'Mauritian rupee',
            self.MVR: 'Maldivian rufiyaa',
            self.MWK: 'Malawian kwacha',
            self.MXN: 'Mexican peso',
            self.MYR: 'Malaysian ringgit',
            self.MZN: 'Mozambican metical',
            self.NAD: 'Namibian dollar',
            self.NGN: 'Nigerian naira',
            self.NIO: 'Nicaraguan córdoba',
            self.NOK: 'Norwegian krone',
            self.NPR: 'Nepalese rupee',
            self.NZD: 'New Zealand dollar',
            self.OMR: 'Omani rial',
            self.PAB: 'Panamanian balboa',
            self.PEN: 'Peruvian sol',
            self.PGK: 'Papua New Guinean kina',
            self.PHP: 'Philippine peso',
            self.PKR: 'Pakistani rupee',
            self.PLN: 'Polish złoty',
            self.PYG: 'Paraguayan guaraní',
            self.QAR: 'Qatari riyal',
            self.RON: 'Romanian leu',
            self.RSD: 'Serbian dinar',
            self.RUB: 'Russian ruble',
            self.RWF: 'Rwandan franc',
            self.SAR: 'Saudi riyal',
            self.SBD: 'Solomon Islands dollar',
            self.SCR: 'Seychellois rupee',
            self.SDG: 'Sudanese pound',
            self.SEK: 'Swedish krona',
            self.SGD: 'Singapore dollar',
            self.SHP: 'Saint Helena pound',
            self.SLE: 'Sierra Leonean leone',
            self.SOS: 'Somali shilling',
            self.SRD: 'Surinamese dollar',
            self.SSP: 'South Sudanese pound',
            self.STN: 'São Tomé and Príncipe dobra',
            self.SYP: 'Syrian pound',
            self.SZL: 'Swazi lilangeni',
            self.THB: 'Thai baht',
            self.TJS: 'Tajikistani somoni',
            self.TMT: 'Turkmenistan manat',
            self.TND: 'Tunisian dinar',
            self.TOP: 'Tongan paʻanga',
            self.TRY: 'Turkish lira',
            self.TTD: 'Trinidad and Tobago dollar',
            self.TVD: 'Tuvaluan dollar',
            self.TWD: 'New Taiwan dollar',
            self.TZS: 'Tanzanian shilling',
            self.UAH: 'Ukrainian hryvnia',
            self.UGX: 'Ugandan shilling',
            self.USD: 'United States dollar',
            self.UYU: 'Uruguayan peso',
            self.UZS: 'Uzbekistani som',
            self.VES: 'Venezuelan bolívar',
            self.VND: 'Vietnamese đồng',
            self.VUV: 'Vanuatu vatu',
            self.WST: 'Samoan tālā',
            self.XAF: 'Central African CFA franc',
            self.XCD: 'East Caribbean dollar',
            self.XDR: 'Special drawing rights',
            self.XOF: 'West African CFA franc',
            self.XPF: 'CFP franc',
            self.YER: 'Yemeni rial',
            self.ZAR: 'South African rand',
            self.ZMW: 'Zambian kwacha',
            self.ZWL: 'Zimbabwean dollar',
        }[self]
