/**
 * API
 * No description provided (generated by Openapi Generator https://github.com/openapitools/openapi-generator)
 *
 * The version of the OpenAPI document: 1.0
 * 
 *
 * NOTE: This class is auto generated by OpenAPI Generator (https://openapi-generator.tech).
 * https://openapi-generator.tech
 * Do not edit the class manually.
 */
import { RecipientInputGenerated } from './recipientInputGenerated';
import { DonorInputGenerated } from './donorInputGenerated';


export interface UploadPatientsGenerated { 
    add_to_existing_patients?: boolean;
    country: UploadPatientsGeneratedCountryEnum;
    donors: Array<DonorInputGenerated>;
    recipients: Array<RecipientInputGenerated>;
    /**
     * The TXM event name has to be provided by an ADMIN.
     */
    txm_event_name: string;
}
export enum UploadPatientsGeneratedCountryEnum {
    Tgo = 'TGO',
    Mne = 'MNE',
    Lao = 'LAO',
    Mrt = 'MRT',
    Nic = 'NIC',
    Lva = 'LVA',
    Omn = 'OMN',
    Afg = 'AFG',
    Cyp = 'CYP',
    Ben = 'BEN',
    Ata = 'ATA',
    Chn = 'CHN',
    Col = 'COL',
    Cxr = 'CXR',
    Atg = 'ATG',
    Msr = 'MSR',
    Mda = 'MDA',
    Zmb = 'ZMB',
    Vnm = 'VNM',
    Atf = 'ATF',
    Tcd = 'TCD',
    Myt = 'MYT',
    Lbn = 'LBN',
    Maf = 'MAF',
    Lux = 'LUX',
    Mtq = 'MTQ',
    Cze = 'CZE',
    Are = 'ARE',
    Cmr = 'CMR',
    Bdi = 'BDI',
    Arg = 'ARG',
    Asm = 'ASM',
    Bhr = 'BHR',
    Chl = 'CHL',
    And = 'AND',
    Mnp = 'MNP',
    Ltu = 'LTU',
    Mdg = 'MDG',
    Lca = 'LCA',
    Tur = 'TUR',
    Ukr = 'UKR',
    Tuv = 'TUV',
    Vir = 'VIR',
    Mlt = 'MLT',
    Nor = 'NOR',
    Mco = 'MCO',
    Che = 'CHE',
    Blm = 'BLM',
    Abw = 'ABW',
    Blz = 'BLZ',
    Bmu = 'BMU',
    Civ = 'CIV',
    Mus = 'MUS',
    Usa = 'USA',
    Twn = 'TWN',
    Yem = 'YEM',
    Mwi = 'MWI',
    Nld = 'NLD',
    Lso = 'LSO',
    Bol = 'BOL',
    Aut = 'AUT',
    Cok = 'COK',
    Blr = 'BLR',
    Aus = 'AUS',
    Brn = 'BRN',
    Mar = 'MAR',
    Nzl = 'NZL',
    Lbr = 'LBR',
    Mdv = 'MDV',
    Tca = 'TCA',
    Uga = 'UGA',
    Tto = 'TTO',
    Pol = 'POL',
    Srb = 'SRB',
    Ind = 'IND',
    Geo = 'GEO',
    Grc = 'GRC',
    Sgs = 'SGS',
    Grd = 'GRD',
    Iot = 'IOT',
    Hkg = 'HKG',
    Prk = 'PRK',
    Kgz = 'KGZ',
    Spm = 'SPM',
    Slv = 'SLV',
    Reu = 'REU',
    Sau = 'SAU',
    Syc = 'SYC',
    Stp = 'STP',
    Ken = 'KEN',
    Imn = 'IMN',
    Kor = 'KOR',
    Guf = 'GUF',
    Dji = 'DJI',
    Gnq = 'GNQ',
    Glp = 'GLP',
    Dnk = 'DNK',
    Ggy = 'GGY',
    Isr = 'ISR',
    Pcn = 'PCN',
    Slb = 'SLB',
    Pry = 'PRY',
    Rus = 'RUS',
    Kwt = 'KWT',
    Dom = 'DOM',
    Gtm = 'GTM',
    Gbr = 'GBR',
    Gum = 'GUM',
    Jey = 'JEY',
    Hmd = 'HMD',
    Sgp = 'SGP',
    Pak = 'PAK',
    Sur = 'SUR',
    Swe = 'SWE',
    Jpn = 'JPN',
    Gnb = 'GNB',
    Esh = 'ESH',
    Dza = 'DZA',
    Gab = 'GAB',
    Fra = 'FRA',
    Dma = 'DMA',
    Hnd = 'HND',
    Sdn = 'SDN',
    Rwa = 'RWA',
    Phl = 'PHL',
    Ssd = 'SSD',
    Qat = 'QAT',
    Per = 'PER',
    Pri = 'PRI',
    Svn = 'SVN',
    Hti = 'HTI',
    Esp = 'ESP',
    Grl = 'GRL',
    Gmb = 'GMB',
    Eri = 'ERI',
    Fin = 'FIN',
    Est = 'EST',
    Kna = 'KNA',
    Hun = 'HUN',
    Irq = 'IRQ',
    Cym = 'CYM',
    Shn = 'SHN',
    Pse = 'PSE',
    Pyf = 'PYF',
    Sjm = 'SJM',
    Idn = 'IDN',
    Isl = 'ISL',
    Egy = 'EGY',
    Flk = 'FLK',
    Fji = 'FJI',
    Gin = 'GIN',
    Guy = 'GUY',
    Irn = 'IRN',
    Com = 'COM',
    Irl = 'IRL',
    Kaz = 'KAZ',
    Rou = 'ROU',
    Svk = 'SVK',
    Png = 'PNG',
    Prt = 'PRT',
    Som = 'SOM',
    Sxm = 'SXM',
    Hrv = 'HRV',
    Kir = 'KIR',
    Jam = 'JAM',
    Ecu = 'ECU',
    Eth = 'ETH',
    Fro = 'FRO',
    Khm = 'KHM',
    Syr = 'SYR',
    Sen = 'SEN',
    Plw = 'PLW',
    Sle = 'SLE',
    Fsm = 'FSM',
    Gib = 'GIB',
    Deu = 'DEU',
    Gha = 'GHA',
    Jor = 'JOR',
    Ita = 'ITA',
    Pan = 'PAN',
    Swz = 'SWZ',
    Smr = 'SMR',
    Tun = 'TUN',
    Mli = 'MLI',
    Cog = 'COG',
    Ala = 'ALA',
    Ago = 'AGO',
    Btn = 'BTN',
    Brb = 'BRB',
    Caf = 'CAF',
    Mmr = 'MMR',
    Lie = 'LIE',
    Nam = 'NAM',
    Moz = 'MOZ',
    Ton = 'TON',
    Vgb = 'VGB',
    Ven = 'VEN',
    Tza = 'TZA',
    Tkm = 'TKM',
    Mex = 'MEX',
    Ncl = 'NCL',
    Mac = 'MAC',
    Lka = 'LKA',
    Cod = 'COD',
    Alb = 'ALB',
    Bwa = 'BWA',
    Cri = 'CRI',
    Bvt = 'BVT',
    Arm = 'ARM',
    Aze = 'AZE',
    Bih = 'BIH',
    Mng = 'MNG',
    Niu = 'NIU',
    Mys = 'MYS',
    Tls = 'TLS',
    Wsm = 'WSM',
    Tha = 'THA',
    Xkx = 'XKX',
    Nfk = 'NFK',
    Lby = 'LBY',
    Aia = 'AIA',
    Bra = 'BRA',
    Cpv = 'CPV',
    Bel = 'BEL',
    Can = 'CAN',
    Bgd = 'BGD',
    Cuw = 'CUW',
    Bhs = 'BHS',
    Nga = 'NGA',
    Mkd = 'MKD',
    Npl = 'NPL',
    Vat = 'VAT',
    Uzb = 'UZB',
    Umi = 'UMI',
    Tkl = 'TKL',
    Vct = 'VCT',
    Zwe = 'ZWE',
    Nru = 'NRU',
    Ner = 'NER',
    Cub = 'CUB',
    Bes = 'BES',
    Bfa = 'BFA',
    Bgr = 'BGR',
    Cck = 'CCK',
    Mhl = 'MHL',
    Zaf = 'ZAF',
    Ury = 'URY',
    Wlf = 'WLF',
    Vut = 'VUT',
    Tjk = 'TJK'
};



