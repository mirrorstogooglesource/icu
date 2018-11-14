# © 2016 and later: Unicode, Inc. and others.
# License & terms of use: http://www.unicode.org/copyright.html#License
CURR_CLDR_VERSION = %version%
# A list of txt's to build
# The downstream packager may not need this file at all if their package is not
# constrained by
# the size (and/or their target OS already has ICU with the full locale data.)
#
# Listed below are locale data files necessary for 40 + 1 + 8 languages Chrome
# is localized to.
#
# In addition to them, 40+ "abridged" locale data files are listed. Chrome is
# localized to them, but
# uses a few categories of data in those locales for IDN handling and language
# name listing (in the UI).
# Aliases which do not have a corresponding xx.xml file (see icu-config.xml &
# build.xml)
CURR_SYNTHETIC_ALIAS =

# All aliases (to not be included under 'installed'), but not including root.
CURR_ALIAS_SOURCE = $(CURR_SYNTHETIC_ALIAS)\
 zh_CN.txt zh_TW.txt zh_HK.txt zh_SG.txt\
 no.txt in.txt iw.txt tl.txt

# Ordinary resources
CURR_SOURCE =\
 am.txt\
 ar.txt ar_AE.txt ar_DJ.txt ar_ER.txt ar_KM.txt\
 ar_LB.txt ar_SA.txt ar_SO.txt ar_SS.txt\
 bg.txt\
 bn.txt\
 ca.txt\
 cs.txt\
 da.txt\
 de.txt de_CH.txt de_LI.txt de_LU.txt\
 el.txt\
 en.txt en_001.txt en_150.txt\
 en_AU.txt en_CA.txt en_GB.txt en_HK.txt en_IN.txt en_NG.txt en_NZ.txt en_SG.txt en_ZA.txt\
 es.txt es_419.txt es_AR.txt es_BO.txt es_BR.txt es_BZ.txt es_CL.txt\
 es_CO.txt es_CR.txt es_CU.txt es_DO.txt es_EC.txt es_GQ.txt es_GT.txt\
 es_HN.txt es_MX.txt es_NI.txt es_PA.txt es_PE.txt es_PH.txt es_PR.txt\
 es_PY.txt es_SV.txt es_US.txt es_UY.txt es_VE.txt\
 et.txt\
 fa.txt\
 fi.txt\
 fil.txt\
 fr.txt fr_CA.txt\
 fr_BI.txt fr_CD.txt fr_DJ.txt fr_DZ.txt fr_GN.txt fr_HT.txt\
 fr_KM.txt fr_LU.txt fr_MG.txt fr_MR.txt fr_MU.txt fr_RW.txt\
 fr_SC.txt fr_SY.txt fr_TN.txt fr_VU.txt\
 gu.txt\
 he.txt\
 hi.txt\
 hr.txt\
 hu.txt\
 id.txt\
 it.txt\
 ja.txt\
 kn.txt\
 ko.txt\
 lt.txt\
 lv.txt\
 ml.txt\
 mr.txt\
 ms.txt\
 nb.txt\
 nl.txt\
 pl.txt\
 pt.txt pt_PT.txt\
 pt_AO.txt pt_CV.txt pt_LU.txt pt_MO.txt pt_MZ.txt pt_ST.txt\
 ro.txt ro_MD.txt\
 ru.txt\
 sk.txt\
 sl.txt\
 sr.txt\
 sv.txt\
 sw.txt sw_CD.txt sw_UG.txt\
 ta.txt\
 te.txt\
 th.txt\
 tr.txt\
 uk.txt\
 vi.txt\
 zh.txt\
 zh_Hans.txt zh_Hans_CN.txt zh_Hans_SG.txt zh_Hans_HK.txt zh_Hans_MO.txt\
 zh_Hant.txt zh_Hant_TW.txt zh_Hant_HK.txt zh_Hant_MO.txt\
 zh_CN.txt zh_TW.txt zh_HK.txt zh_MO.txt zh_SG.txt
