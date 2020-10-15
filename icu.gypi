# Copyright 2013 The Chromium Authors. All rights reserved.
# Use of this source code is governed by a BSD-style license that can be
# found in the LICENSE file.

{
  'variables': {
# find  source/i18n -maxdepth 1  ! -type d  | egrep  '\.(c|cpp)$' | \
# sort | sed "s/^\(.*\)$/      '\1',/"
    'icui18n_sources': [
      # I18N_SRC_START
      'source/i18n/alphaindex.cpp',
      'source/i18n/anytrans.cpp',
      'source/i18n/astro.cpp',
      'source/i18n/basictz.cpp',
      'source/i18n/bocsu.cpp',
      'source/i18n/brktrans.cpp',
      'source/i18n/buddhcal.cpp',
      'source/i18n/calendar.cpp',
      'source/i18n/casetrn.cpp',
      'source/i18n/cecal.cpp',
      'source/i18n/chnsecal.cpp',
      'source/i18n/choicfmt.cpp',
      'source/i18n/coleitr.cpp',
      'source/i18n/collationbuilder.cpp',
      'source/i18n/collationcompare.cpp',
      'source/i18n/collation.cpp',
      'source/i18n/collationdatabuilder.cpp',
      'source/i18n/collationdata.cpp',
      'source/i18n/collationdatareader.cpp',
      'source/i18n/collationdatawriter.cpp',
      'source/i18n/collationfastlatinbuilder.cpp',
      'source/i18n/collationfastlatin.cpp',
      'source/i18n/collationfcd.cpp',
      'source/i18n/collationiterator.cpp',
      'source/i18n/collationkeys.cpp',
      'source/i18n/collationroot.cpp',
      'source/i18n/collationrootelements.cpp',
      'source/i18n/collationruleparser.cpp',
      'source/i18n/collationsets.cpp',
      'source/i18n/collationsettings.cpp',
      'source/i18n/collationtailoring.cpp',
      'source/i18n/collationweights.cpp',
      'source/i18n/coll.cpp',
      'source/i18n/compactdecimalformat.cpp',
      'source/i18n/coptccal.cpp',
      'source/i18n/cpdtrans.cpp',
      'source/i18n/csdetect.cpp',
      'source/i18n/csmatch.cpp',
      'source/i18n/csr2022.cpp',
      'source/i18n/csrecog.cpp',
      'source/i18n/csrmbcs.cpp',
      'source/i18n/csrsbcs.cpp',
      'source/i18n/csrucode.cpp',
      'source/i18n/csrutf8.cpp',
      'source/i18n/curramt.cpp',
      'source/i18n/currfmt.cpp',
      'source/i18n/currpinf.cpp',
      'source/i18n/currunit.cpp',
      'source/i18n/dangical.cpp',
      'source/i18n/datefmt.cpp',
      'source/i18n/dayperiodrules.cpp',
      'source/i18n/dcfmtsym.cpp',
      'source/i18n/decContext.cpp',
      'source/i18n/decimfmt.cpp',
      'source/i18n/decNumber.cpp',
      'source/i18n/double-conversion-bignum.cpp',
      'source/i18n/double-conversion-bignum-dtoa.cpp',
      'source/i18n/double-conversion-cached-powers.cpp',
      'source/i18n/double-conversion-double-to-string.cpp',
      'source/i18n/double-conversion-fast-dtoa.cpp',
      'source/i18n/double-conversion-string-to-double.cpp',
      'source/i18n/double-conversion-strtod.cpp',
      'source/i18n/dtfmtsym.cpp',
      'source/i18n/dtitvfmt.cpp',
      'source/i18n/dtitvinf.cpp',
      'source/i18n/dtptngen.cpp',
      'source/i18n/dtrule.cpp',
      'source/i18n/erarules.cpp',
      'source/i18n/esctrn.cpp',
      'source/i18n/ethpccal.cpp',
      'source/i18n/fmtable_cnv.cpp',
      'source/i18n/fmtable.cpp',
      'source/i18n/format.cpp',
      'source/i18n/formatted_string_builder.cpp',
      'source/i18n/formattedval_iterimpl.cpp',
      'source/i18n/formattedval_sbimpl.cpp',
      'source/i18n/formattedvalue.cpp',
      'source/i18n/fphdlimp.cpp',
      'source/i18n/fpositer.cpp',
      'source/i18n/funcrepl.cpp',
      'source/i18n/gender.cpp',
      'source/i18n/gregocal.cpp',
      'source/i18n/gregoimp.cpp',
      'source/i18n/hebrwcal.cpp',
      'source/i18n/indiancal.cpp',
      'source/i18n/inputext.cpp',
      'source/i18n/islamcal.cpp',
      'source/i18n/japancal.cpp',
      'source/i18n/listformatter.cpp',
      'source/i18n/measfmt.cpp',
      'source/i18n/measunit.cpp',
      'source/i18n/measunit_extra.cpp',
      'source/i18n/measure.cpp',
      'source/i18n/msgfmt.cpp',
      'source/i18n/name2uni.cpp',
      'source/i18n/nfrs.cpp',
      'source/i18n/nfrule.cpp',
      'source/i18n/nfsubs.cpp',
      'source/i18n/nortrans.cpp',
      'source/i18n/nultrans.cpp',
      'source/i18n/number_affixutils.cpp',
      'source/i18n/number_asformat.cpp',
      'source/i18n/number_capi.cpp',
      'source/i18n/number_compact.cpp',
      'source/i18n/number_currencysymbols.cpp',
      'source/i18n/number_decimalquantity.cpp',
      'source/i18n/number_decimfmtprops.cpp',
      'source/i18n/number_fluent.cpp',
      'source/i18n/number_formatimpl.cpp',
      'source/i18n/number_grouping.cpp',
      'source/i18n/number_integerwidth.cpp',
      'source/i18n/number_longnames.cpp',
      'source/i18n/number_mapper.cpp',
      'source/i18n/number_modifiers.cpp',
      'source/i18n/number_multiplier.cpp',
      'source/i18n/number_notation.cpp',
      'source/i18n/number_output.cpp',
      'source/i18n/number_padding.cpp',
      'source/i18n/number_patternmodifier.cpp',
      'source/i18n/number_patternstring.cpp',
      'source/i18n/number_rounding.cpp',
      'source/i18n/number_scientific.cpp',
      'source/i18n/number_skeletons.cpp',
      'source/i18n/number_symbolswrapper.cpp',
      'source/i18n/number_usageprefs.cpp',
      'source/i18n/number_utils.cpp',
      'source/i18n/numfmt.cpp',
      'source/i18n/numparse_affixes.cpp',
      'source/i18n/numparse_compositions.cpp',
      'source/i18n/numparse_currency.cpp',
      'source/i18n/numparse_decimal.cpp',
      'source/i18n/numparse_impl.cpp',
      'source/i18n/numparse_parsednumber.cpp',
      'source/i18n/numparse_scientific.cpp',
      'source/i18n/numparse_symbols.cpp',
      'source/i18n/numparse_validators.cpp',
      'source/i18n/numrange_capi.cpp',
      'source/i18n/numrange_fluent.cpp',
      'source/i18n/numrange_impl.cpp',
      'source/i18n/numsys.cpp',
      'source/i18n/olsontz.cpp',
      'source/i18n/persncal.cpp',
      'source/i18n/pluralranges.cpp',
      'source/i18n/plurfmt.cpp',
      'source/i18n/plurrule.cpp',
      'source/i18n/quant.cpp',
      'source/i18n/quantityformatter.cpp',
      'source/i18n/rbnf.cpp',
      'source/i18n/rbt.cpp',
      'source/i18n/rbt_data.cpp',
      'source/i18n/rbt_pars.cpp',
      'source/i18n/rbt_rule.cpp',
      'source/i18n/rbt_set.cpp',
      'source/i18n/rbtz.cpp',
      'source/i18n/regexcmp.cpp',
      'source/i18n/regeximp.cpp',
      'source/i18n/regexst.cpp',
      'source/i18n/regextxt.cpp',
      'source/i18n/region.cpp',
      'source/i18n/reldatefmt.cpp',
      'source/i18n/reldtfmt.cpp',
      'source/i18n/rematch.cpp',
      'source/i18n/remtrans.cpp',
      'source/i18n/repattrn.cpp',
      'source/i18n/rulebasedcollator.cpp',
      'source/i18n/scientificnumberformatter.cpp',
      'source/i18n/scriptset.cpp',
      'source/i18n/search.cpp',
      'source/i18n/selfmt.cpp',
      'source/i18n/sharedbreakiterator.cpp',
      'source/i18n/simpletz.cpp',
      'source/i18n/smpdtfmt.cpp',
      'source/i18n/smpdtfst.cpp',
      'source/i18n/sortkey.cpp',
      'source/i18n/standardplural.cpp',
      'source/i18n/string_segment.cpp',
      'source/i18n/strmatch.cpp',
      'source/i18n/strrepl.cpp',
      'source/i18n/stsearch.cpp',
      'source/i18n/taiwncal.cpp',
      'source/i18n/timezone.cpp',
      'source/i18n/titletrn.cpp',
      'source/i18n/tmunit.cpp',
      'source/i18n/tmutamt.cpp',
      'source/i18n/tmutfmt.cpp',
      'source/i18n/tolowtrn.cpp',
      'source/i18n/toupptrn.cpp',
      'source/i18n/translit.cpp',
      'source/i18n/transreg.cpp',
      'source/i18n/tridpars.cpp',
      'source/i18n/tzfmt.cpp',
      'source/i18n/tzgnames.cpp',
      'source/i18n/tznames.cpp',
      'source/i18n/tznames_impl.cpp',
      'source/i18n/tzrule.cpp',
      'source/i18n/tztrans.cpp',
      'source/i18n/ucal.cpp',
      'source/i18n/ucln_in.cpp',
      'source/i18n/ucol.cpp',
      'source/i18n/ucoleitr.cpp',
      'source/i18n/ucol_res.cpp',
      'source/i18n/ucol_sit.cpp',
      'source/i18n/ucsdet.cpp',
      'source/i18n/udat.cpp',
      'source/i18n/udateintervalformat.cpp',
      'source/i18n/udatpg.cpp',
      'source/i18n/ufieldpositer.cpp',
      'source/i18n/uitercollationiterator.cpp',
      'source/i18n/ulistformatter.cpp',
      'source/i18n/ulocdata.cpp',
      'source/i18n/umsg.cpp',
      'source/i18n/unesctrn.cpp',
      'source/i18n/uni2name.cpp',
      'source/i18n/units_complexconverter.cpp',
      'source/i18n/units_converter.cpp',
      'source/i18n/units_data.cpp',
      'source/i18n/units_router.cpp',
      'source/i18n/unum.cpp',
      'source/i18n/unumsys.cpp',
      'source/i18n/upluralrules.cpp',
      'source/i18n/uregexc.cpp',
      'source/i18n/uregex.cpp',
      'source/i18n/uregion.cpp',
      'source/i18n/usearch.cpp',
      'source/i18n/uspoof_build.cpp',
      'source/i18n/uspoof_conf.cpp',
      'source/i18n/uspoof.cpp',
      'source/i18n/uspoof_impl.cpp',
      'source/i18n/utf16collationiterator.cpp',
      'source/i18n/utf8collationiterator.cpp',
      'source/i18n/utmscale.cpp',
      'source/i18n/utrans.cpp',
      'source/i18n/vtzone.cpp',
      'source/i18n/vzone.cpp',
      'source/i18n/windtfmt.cpp',
      'source/i18n/winnmfmt.cpp',
      'source/i18n/wintzimpl.cpp',
      'source/i18n/zonemeta.cpp',
      'source/i18n/zrule.cpp',
      'source/i18n/ztrans.cpp',
      # I18N_SRC_END
    ],
    'icuuc_sources': [
# find  source/common -maxdepth 1  ! -type d  | egrep  '\.(c|cpp)$' | \
# sort | sed "s/^\(.*\)$/      '\1',/"
      # COMMON_SRC_START
      'source/common/appendable.cpp',
      'source/common/bmpset.cpp',
      'source/common/brkeng.cpp',
      'source/common/brkiter.cpp',
      'source/common/bytesinkutil.cpp',
      'source/common/bytestream.cpp',
      'source/common/bytestriebuilder.cpp',
      'source/common/bytestrie.cpp',
      'source/common/bytestrieiterator.cpp',
      'source/common/caniter.cpp',
      'source/common/characterproperties.cpp',
      'source/common/chariter.cpp',
      'source/common/charstr.cpp',
      'source/common/cmemory.cpp',
      'source/common/cstr.cpp',
      'source/common/cstring.cpp',
      'source/common/cwchar.cpp',
      'source/common/dictbe.cpp',
      'source/common/dictionarydata.cpp',
      'source/common/dtintrv.cpp',
      'source/common/edits.cpp',
      'source/common/errorcode.cpp',
      'source/common/filteredbrk.cpp',
      'source/common/filterednormalizer2.cpp',
      'source/common/icudataver.cpp',
      'source/common/icuplug.cpp',
      'source/common/loadednormalizer2impl.cpp',
      'source/common/localebuilder.cpp',
      'source/common/localematcher.cpp',
      'source/common/localeprioritylist.cpp',
      'source/common/locavailable.cpp',
      'source/common/locbased.cpp',
      'source/common/locdispnames.cpp',
      'source/common/locdistance.cpp',
      'source/common/locdspnm.cpp',
      'source/common/locid.cpp',
      'source/common/loclikely.cpp',
      'source/common/loclikelysubtags.cpp',
      'source/common/locmap.cpp',
      'source/common/locresdata.cpp',
      'source/common/locutil.cpp',
      'source/common/lsr.cpp',
      'source/common/messagepattern.cpp',
      'source/common/normalizer2.cpp',
      'source/common/normalizer2impl.cpp',
      'source/common/normlzr.cpp',
      'source/common/parsepos.cpp',
      'source/common/patternprops.cpp',
      'source/common/pluralmap.cpp',
      'source/common/propname.cpp',
      'source/common/propsvec.cpp',
      'source/common/punycode.cpp',
      'source/common/putil.cpp',
      'source/common/rbbi_cache.cpp',
      'source/common/rbbi.cpp',
      'source/common/rbbidata.cpp',
      'source/common/rbbinode.cpp',
      'source/common/rbbirb.cpp',
      'source/common/rbbiscan.cpp',
      'source/common/rbbisetb.cpp',
      'source/common/rbbistbl.cpp',
      'source/common/rbbitblb.cpp',
      'source/common/resbund_cnv.cpp',
      'source/common/resbund.cpp',
      'source/common/resource.cpp',
      'source/common/restrace.cpp',
      'source/common/ruleiter.cpp',
      'source/common/schriter.cpp',
      'source/common/serv.cpp',
      'source/common/servlk.cpp',
      'source/common/servlkf.cpp',
      'source/common/servls.cpp',
      'source/common/servnotf.cpp',
      'source/common/servrbf.cpp',
      'source/common/servslkf.cpp',
      'source/common/sharedobject.cpp',
      'source/common/simpleformatter.cpp',
      'source/common/static_unicode_sets.cpp',
      'source/common/stringpiece.cpp',
      'source/common/stringtriebuilder.cpp',
      'source/common/uarrsort.cpp',
      'source/common/ubidi.cpp',
      'source/common/ubidiln.cpp',
      'source/common/ubidi_props.cpp',
      'source/common/ubiditransform.cpp',
      'source/common/ubidiwrt.cpp',
      'source/common/ubrk.cpp',
      'source/common/ucase.cpp',
      'source/common/ucasemap.cpp',
      'source/common/ucasemap_titlecase_brkiter.cpp',
      'source/common/ucat.cpp',
      'source/common/uchar.cpp',
      'source/common/ucharstriebuilder.cpp',
      'source/common/ucharstrie.cpp',
      'source/common/ucharstrieiterator.cpp',
      'source/common/uchriter.cpp',
      'source/common/ucln_cmn.cpp',
      'source/common/ucmndata.cpp',
      'source/common/ucnv2022.cpp',
      'source/common/ucnv_bld.cpp',
      'source/common/ucnvbocu.cpp',
      'source/common/ucnv_cb.cpp',
      'source/common/ucnv_cnv.cpp',
      'source/common/ucnv.cpp',
      'source/common/ucnv_ct.cpp',
      'source/common/ucnvdisp.cpp',
      'source/common/ucnv_err.cpp',
      'source/common/ucnv_ext.cpp',
      'source/common/ucnvhz.cpp',
      'source/common/ucnv_io.cpp',
      'source/common/ucnvisci.cpp',
      'source/common/ucnvlat1.cpp',
      'source/common/ucnv_lmb.cpp',
      'source/common/ucnvmbcs.cpp',
      'source/common/ucnvscsu.cpp',
      'source/common/ucnvsel.cpp',
      'source/common/ucnv_set.cpp',
      'source/common/ucnv_u16.cpp',
      'source/common/ucnv_u32.cpp',
      'source/common/ucnv_u7.cpp',
      'source/common/ucnv_u8.cpp',
      'source/common/ucol_swp.cpp',
      'source/common/ucptrie.cpp',
      'source/common/ucurr.cpp',
      'source/common/udata.cpp',
      'source/common/udatamem.cpp',
      'source/common/udataswp.cpp',
      'source/common/uenum.cpp',
      'source/common/uhash.cpp',
      'source/common/uhash_us.cpp',
      'source/common/uidna.cpp',
      'source/common/uinit.cpp',
      'source/common/uinvchar.cpp',
      'source/common/uiter.cpp',
      'source/common/ulist.cpp',
      'source/common/uloc.cpp',
      'source/common/uloc_keytype.cpp',
      'source/common/uloc_tag.cpp',
      'source/common/umapfile.cpp',
      'source/common/umath.cpp',
      'source/common/umutablecptrie.cpp',
      'source/common/umutex.cpp',
      'source/common/unames.cpp',
      'source/common/unifiedcache.cpp',
      'source/common/unifilt.cpp',
      'source/common/unifunct.cpp',
      'source/common/uniset_closure.cpp',
      'source/common/uniset.cpp',
      'source/common/uniset_props.cpp',
      'source/common/unisetspan.cpp',
      'source/common/unistr_case.cpp',
      'source/common/unistr_case_locale.cpp',
      'source/common/unistr_cnv.cpp',
      'source/common/unistr.cpp',
      'source/common/unistr_props.cpp',
      'source/common/unistr_titlecase_brkiter.cpp',
      'source/common/unormcmp.cpp',
      'source/common/unorm.cpp',
      'source/common/uobject.cpp',
      'source/common/uprops.cpp',
      'source/common/uresbund.cpp',
      'source/common/ures_cnv.cpp',
      'source/common/uresdata.cpp',
      'source/common/usc_impl.cpp',
      'source/common/uscript.cpp',
      'source/common/uscript_props.cpp',
      'source/common/uset.cpp',
      'source/common/usetiter.cpp',
      'source/common/uset_props.cpp',
      'source/common/ushape.cpp',
      'source/common/usprep.cpp',
      'source/common/ustack.cpp',
      'source/common/ustrcase.cpp',
      'source/common/ustrcase_locale.cpp',
      'source/common/ustr_cnv.cpp',
      'source/common/ustrenum.cpp',
      'source/common/ustrfmt.cpp',
      'source/common/ustring.cpp',
      'source/common/ustr_titlecase_brkiter.cpp',
      'source/common/ustrtrns.cpp',
      'source/common/ustr_wcs.cpp',
      'source/common/utext.cpp',
      'source/common/utf_impl.cpp',
      'source/common/util.cpp',
      'source/common/util_props.cpp',
      'source/common/utrace.cpp',
      'source/common/utrie2_builder.cpp',
      'source/common/utrie2.cpp',
      'source/common/utrie.cpp',
      'source/common/utrie_swap.cpp',
      'source/common/uts46.cpp',
      'source/common/utypes.cpp',
      'source/common/uvector.cpp',
      'source/common/uvectr32.cpp',
      'source/common/uvectr64.cpp',
      'source/common/wintz.cpp',
      # COMMON_SRC_END
    ]
  }
}
