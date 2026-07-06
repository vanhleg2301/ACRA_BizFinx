"""
ACRA taxonomy namespace URIs and schema locations.
These values come from the Full_XBRL_2026_v1.0 taxonomy.
If ACRA updates the taxonomy, update the URLs here — nowhere else.
"""

# Namespace URI map: prefix → URI
NS = {
    "xbrli":    "http://www.xbrl.org/2003/instance",
    "link":     "http://www.xbrl.org/2003/linkbase",
    "xlink":    "http://www.w3.org/1999/xlink",
    "xsi":      "http://www.w3.org/2001/XMLSchema-instance",
    "iso4217":  "http://www.xbrl.org/2003/iso4217",
    "xs":       "http://www.w3.org/2001/XMLSchema",
    "sg-as":    "http://www.acra.gov.sg/taxonomy/2026/sg-as",
    "sg-dei":   "http://www.acra.gov.sg/taxonomy/2026/sg-dei",
    "sg-ca":    "http://www.acra.gov.sg/taxonomy/2026/sg-ca",
    "sg-ssa":   "http://www.acra.gov.sg/taxonomy/2026/sg-ssa",
}

# Base URLs for ACRA taxonomy XSD files (referenced in company .xsd)
TAXONOMY_BASE = "http://www.acra.gov.sg/taxonomy/2026"
ACRA_ENTITY_SCHEME = "http://www.acra.gov.sg"

# Linkbase role URIs
LB_ROLES = {
    "presentation": "http://www.xbrl.org/2003/role/presentationLinkbaseRef",
    "calculation":  "http://www.xbrl.org/2003/role/calculationLinkbaseRef",
    "definition":   "http://www.xbrl.org/2003/role/definitionLinkbaseRef",
    "label":        "http://www.xbrl.org/2003/role/labelLinkbaseRef",
}

# Elements that carry non-numeric (string/date/boolean) values → no unitRef
TEXT_ELEMENTS = {
    "NameOfCompany", "UniqueEntityNumber", "CurrentPeriodStartDate",
    "CurrentPeriodEndDate", "PriorPeriodStartDate", "TypeOfXBRLFiling",
    "NatureOfFinancialStatementsCompanyLevelOrConsolidated",
    "TypeOfAccountingStandardUsedToPrepareFinancialStatements",
    "DateOfAuthorisationForIssueOfFinancialStatements",
    "TypeOfStatementOfFinancialPosition",
    "WhetherFinancialStatementsArePreparedOnGoingConcernBasis",
    "WhetherThereAreChangesToComparativeAmountsDueToRestatementsReclassificationOrOtherReasons",
    "DescriptionOfPresentationCurrency", "DescriptionOfFunctionalCurrency",
    "LevelOfRoundingUsedInFinancialStatements",
    "DescriptionOfNatureOfEntitysOperationsAndPrincipalActivities",
    "PrincipalPlaceOfBusiness",
    "PrincipalPlaceOfBusinessIfDifferentFromRegisteredOffice",
    "WhetherCompanyOrGroupIfConsolidatedAccountsArePreparedHasMoreThan50Employees",
    "TaxonomyVersion", "NameAndVersionOfSoftwareUsedToGenerateInstanceDocument",
    "HowWasXBRLInstanceDocumentPrepared",
    "WhetherInDirectorsOpinionFinancialStatementsAreDrawnUpSoAsToExhibitATrueAndFairView",
    "WhetherThereAreReasonableGroundsToBelieveThatCompanyWillBeAbleToPayItsDebtsAsAndWhenTheyFallDueAtDateOfStatement",
    "TypeOfAuditOpinionInIndependentAuditorsReport",
    "NumberOfEmployeesOfCompany", "NumberOfEmployeesOfGroup",
    "WhetherCompanyIsSubsidiary", "WhetherCompanyHasAnySubsidiaryAssociateOrJointVenture",
    "WhetherCompanyHasOverseasInvestmentsInSubsidiariesAssociatesOrJointVentures",
    "DisclosureOfCompleteSetOfFinancialStatementsTextBlock",
    "PriorPeriodEndDate",
    "PrincipalPlaceOfBusiness",
}
