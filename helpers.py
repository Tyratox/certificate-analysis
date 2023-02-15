import pandas as pd
from cryptography import x509
import time
import datetime
from typing import Tuple, List, Any


def is_valid_input_file(filename: str):

    # ignore system files
    if filename.startswith("."):
        return False

    # only read gzip compressed csv files
    if not filename.endswith(".gz"):
        return False

    return True


def map_certificate_version(cert: x509.Certificate):
    try:
        if cert.version == x509.Version.v1:
            return "v1"
        elif cert.version == x509.Version.v3:
            return "v3"
        else:
            return "unkown"
    except x509.InvalidVersion:
        return "unkown"


def map_certificate_datetime(dt: datetime.datetime):
    # convert to unix timestamp
    return time.mktime(dt.timetuple())


# get all name object identifier names
names_object_identifier_names = [
    a for a in dir(x509.NameOID)
    if not a.startswith('__') and
    isinstance(getattr(x509.NameOID, a), x509.ObjectIdentifier)
]


def map_certificate_name(name: x509.Name):

    # then extract all name attribures from the x509.Name
    name_attributes = [
        name.get_attributes_for_oid(getattr(x509.NameOID, n))
        for n in names_object_identifier_names
    ]

    # check if for one of the object identifiers there are multiple values
    for i, name_attribute in enumerate(name_attributes):
        if len(name_attribute) > 1:
            print(name)
            print(name_attribute)
            raise Exception(
                f"Unexpected data: multiple name attribute values found for {names_object_identifier_names[i]}"
            )

    # if not, map all of them to the first value or None
    name_attributes = [
        na[0].value if len(na) > 0 else None
        for na in name_attributes
    ]

    return name_attributes


# get all signature algorithm object identifier names
signature_algorithm_object_identifier_names = [
    a for a in dir(x509.SignatureAlgorithmOID)
    if not a.startswith('__') and
    isinstance(getattr(x509.SignatureAlgorithmOID, a), x509.ObjectIdentifier)
]


def map_certificate_signature_algorithm_oid(oid: x509.ObjectIdentifier):
    for name in signature_algorithm_object_identifier_names:
        if getattr(x509.SignatureAlgorithmOID, name) == oid:
            return name

    return "unknown"


# get all certificate extension object identifier names
extension_object_identifier_names = [
    a for a in dir(x509.ExtensionOID)
    if not a.startswith('__') and
    isinstance(getattr(x509.ExtensionOID, a), x509.ObjectIdentifier)
]

# get all ExtendedKeyUsage object identifier names
extended_key_usage_object_identifier_names = [
    a for a in dir(x509.ExtendedKeyUsageOID)
    if not a.startswith('__') and
    isinstance(getattr(x509.ExtendedKeyUsageOID, a), x509.ObjectIdentifier)
]


def map_certificate_extension(name: str, extensions: x509.Extensions, oid: x509.ObjectIdentifier) -> List[Tuple[str, Any]]:
    try:
        extension = extensions.get_extension_for_oid(oid).value
        if isinstance(extension, x509.BasicConstraints):
          # Basic constraints is an X.509 extension type that defines whether a
          # given certificate is allowed to sign additional certificates and
          # what path length restrictions may exist.
          # (https://cryptography.io/en/latest/x509/reference/#cryptography.x509.BasicConstraints)
            return [
                (name + "_CA", extension.ca),
                (name + "_PATH_LENGTH", extension.path_length),
            ]
        elif isinstance(extension, x509.KeyUsage):
          # The key usage extension defines the purpose of the key contained in
          # the certificate. The usage restriction might be employed when a key
          # that could be used for more than one operation is to be restricted.
          # (https://cryptography.io/en/latest/x509/reference/#cryptography.x509.KeyUsage)
            return [
                (name + "_DIGITAL_SIGNATURE", extension.digital_signature),
                (name + "_CONTENT_COMMITMENT", extension.content_commitment),
                (name + "_KEY_ENCIPHERMENT", extension.key_encipherment),
                (name + "_DATA_ENCIPHERMENT", extension.data_encipherment),
                (name + "_KEY_AGREEMENT", extension.key_agreement),
                (name + "_KEY_CERT_SIGN", extension.key_cert_sign),
                (name + "_CRL_SIGN", extension.crl_sign),
                # encipher_only is undefined unless key_agreement is true
                (
                    name + "_ENCIPHER_ONLY",
                    extension.encipher_only if extension.key_agreement else False
                ),
                # decipher_only is undefined unless key_agreement is true
                (
                    name + "_DECIPHER_ONLY",
                    extension.decipher_only if extension.key_agreement else False
                ),
            ]
        elif isinstance(extension, x509.SubjectAlternativeName) or isinstance(extension, x509.IssuerAlternativeName):
          # Subject alternative name is an X.509 extension that provides a list
          # of general name instances that provide a set of identities for which
          # the certificate is valid. The object is iterable to get every
          # element.
          # (https://cryptography.io/en/latest/x509/reference/#cryptography.x509.SubjectAlternativeName)
            return [(name, extension.get_values_for_type(x509.GeneralName))]
        elif isinstance(extension, x509.IssuerAlternativeName):
          # Issuer alternative name is an X.509 extension that provides a list of
          # general name instances that provide a set of identities for the
          # certificate issuer. The object is iterable to get every element.
          # (https://cryptography.io/en/latest/x509/reference/#cryptography.x509.IssuerAlternativeName)
            return [(name, extension.get_values_for_type(x509.GeneralName))]
        elif isinstance(extension, x509.SubjectKeyIdentifier):
            # The subject key identifier extension provides a means of
            # identifying certificates that contain a particular public key.
            # (https://cryptography.io/en/latest/x509/reference/#cryptography.x509.SubjectKeyIdentifier)

            # just a byte value encoding the key -> no interesting for us
            return []
        elif isinstance(extension, x509.NameConstraints):
            # The name constraints extension, which only has meaning in a CA
            # certificate, defines a name space within which all subject names
            # in certificates issued beneath the CA certificate must (or must
            # not) be in. For specific details on the way this extension should
            # be processed see RFC 5280.
            # (https://cryptography.io/en/latest/x509/reference/#cryptography.x509.NameConstraints)

            # restricts how a CA certificate can be used -> not interesting for us
            return []
        elif isinstance(extension, x509.CRLDistributionPoints):
            # The CRL distribution points extension identifies how CRL information
            # is obtained. It is an iterable, containing one or more
            # DistributionPoint instances.
            # (https://cryptography.io/en/latest/x509/reference/#cryptography.x509.CRLDistributionPoints)

            # the actual distribution points are not interesting to us but count might be
            return [(name + "_COUNT", len(extension._distribution_points))]
        elif isinstance(extension, x509.CertificatePolicies):
            # The certificate policies extension is an iterable, containing one or
            # more PolicyInformation instances.
            # (https://cryptography.io/en/latest/x509/reference/#cryptography.x509.CertificatePolicies)

            # the exact policies are not of interest (yet) but the count might be
            return [(name + "_COUNT", len(extension._policies))]
        elif isinstance(extension, x509.AuthorityKeyIdentifier):
            # The authority key identifier extension provides a means of
            # identifying the public key corresponding to the private key used
            # to sign a certificate. This extension is typically used to assist
            # in determining the appropriate certificate chain. For more
            # information about generation and use of this extension see RFC
            # 5280 section 4.2.1.1.
            # (https://cryptography.io/en/latest/x509/reference/#cryptography.x509.AuthorityKeyIdentifier)

            # again a key identifier -> not interesting to us
            return []
        elif isinstance(extension, x509.ExtendedKeyUsage):
            # This extension indicates one or more purposes for which the
            # certified public key may be used, in addition to or in place of the
            # basic purposes indicated in the key usage extension. The object is
            # iterable to obtain the list of ExtendedKeyUsageOID OIDs present.
            # (https://cryptography.io/en/latest/x509/reference/#cryptography.x509.ExtendedKeyUsage)

            # for each possible extended key usage return a true / false flag
            return [
                (name + "_" + oid, getattr(x509.ExtendedKeyUsageOID, oid)
                 in extension._usages)
                for oid in extended_key_usage_object_identifier_names
            ]
        elif isinstance(extension, x509.AuthorityInformationAccess):
            # The authority information access extension indicates how to access
            # information and services for the issuer of the certificate in
            # which the extension appears. Information and services may include
            # online validation services (such as OCSP) and issuer data. It is
            # an iterable, containing one or more AccessDescription instances.
            # (https://cryptography.io/en/latest/x509/reference/#cryptography.x509.AuthorityInformationAccess)

            # the values are not interesting and probably neither their existence
            return []
            # return [
            #     (name + "_OSCP", x509.AuthorityInformationAccessOID.OCSP in extension._descriptions),
            #     (name + "_CA_ISSUERS",
            #      x509.AuthorityInformationAccessOID.CA_ISSUERS in extension._descriptions),
            # ]
        elif isinstance(extension, x509.SubjectInformationAccess):
            # The subject information access extension indicates how to access
            # information and services for the subject of the certificate in
            # which the extension appears. When the subject is a CA, information
            # and services may include certificate validation services and CA
            # policy data. When the subject is an end entity, the information
            # describes the type of services offered and how to access them. It
            # is an iterable, containing one or more AccessDescription
            # instances.
            # (https://cryptography.io/en/latest/x509/reference/#cryptography.x509.SubjectInformationAccess)

            # according to https://cryptography.io/en/latest/x509/reference/#cryptography.x509.AccessDescription
            # this can only contain one possible value, it's value is certainly not interesting and probably neither
            # it's existence
            return []
        elif isinstance(extension, x509.InhibitAnyPolicy):
            # The inhibit anyPolicy extension indicates that the special OID
            # ANY_POLICY, is not considered an explicit match for other
            # CertificatePolicies except when it appears in an intermediate
            # self-issued CA certificate. The value indicates the number of
            # additional non-self-issued certificates that may appear in the path
            # before ANY_POLICY is no longer permitted. For example, a value of
            # one indicates that ANY_POLICY may be processed in certificates
            # issued by the subject of this certificate, but not in additional
            # certificates in the path.

            # maybe interesting?
            return [(name, extension.skip_certs)]
        elif isinstance(extension, x509.OCSPNoCheck):
            # This presence of this extension indicates that an OCSP client can
            # trust a responder for the lifetime of the responder’s certificate.
            # CAs issuing such a certificate should realize that a compromise of
            # the responder’s key is as serious as the compromise of a CA key
            # used to sign CRLs, at least for the validity period of this
            # certificate. CA’s may choose to issue this type of certificate
            # with a very short lifetime and renew it frequently. This extension
            # is only relevant when the certificate is an authorized OCSP
            # responder.

            # most certainly interesting!
            return [(name, True)]
        elif isinstance(extension, x509.TLSFeature):
            # The TLS Feature extension is defined in RFC 7633 and is used in
            # certificates for OCSP Must-Staple. The object is iterable to get
            # every element.

            # existence might be interesting to check how many use stapling
            return [(name, True)]
        elif isinstance(extension, x509.CRLNumber):
            # The CRL number is a CRL extension that conveys a monotonically
            # increasing sequence number for a given CRL scope and CRL issuer.
            # This extension allows users to easily determine when a particular
            # CRL supersedes another CRL. RFC 5280 requires that this extension
            # be present in conforming CRLs.
            # (https://cryptography.io/en/latest/x509/reference/#cryptography.x509.CRLNumber)

            # interesting -> might be correlated with number of revoked certificates
            return [(name, extension.crl_number)]
        elif isinstance(extension, x509.DeltaCRLIndicator):
            # The delta CRL indicator is a CRL extension that identifies a CRL
            # as being a delta CRL. Delta CRLs contain updates to revocation
            # information previously distributed, rather than all the
            # information that would appear in a complete CRL.
            # (https://cryptography.io/en/latest/x509/reference/#cryptography.x509.DeltaCRLIndicator)

            # existence might be interesting as it is not expected to show up anywhere
            return [(name, True)]
        elif isinstance(extension, x509.PrecertificateSignedCertificateTimestamps):
            # This extension contains SignedCertificateTimestamp instances which
            # were issued for the pre-certificate corresponding to this
            # certificate. These can be used to verify that the certificate is
            # included in a public Certificate Transparency log.

            # given we retrieved the certificates from the CT logs this value should
            # be an interesting sanity check
            return [(name, len(extension._signed_certificate_timestamps))]
        elif isinstance(extension, x509.PrecertPoison):
            # This extension indicates that the certificate should not be
            # treated as a certificate for the purposes of validation, but is
            # instead for submission to a certificate transparency log in order
            # to obtain SCTs which will be embedded in a
            # PrecertificateSignedCertificateTimestamps extension on the final
            # certificate.

            # I would expect this to be set of all of them since we retrieved them from CT logs
            # -> verify
            return [(name, True)]
        elif isinstance(extension, x509.SignedCertificateTimestamps):
            # This extension contains SignedCertificateTimestamp instances.
            # These can be used to verify that the certificate is included in a
            # public Certificate Transparency log. This extension is only found
            # in OCSP responses. For SCTs in an X.509 certificate see
            # PrecertificateSignedCertificateTimestamps.
            # (https://cryptography.io/en/latest/x509/reference/#cryptography.x509.PrecertificateSignedCertificateTimestamps)

            # accroding to the description this should not be present in any certificates retrieved
            # from a CT log
            return [(name, True)]
        elif isinstance(extension, x509.PolicyConstraints):
            # The policy constraints extension is used to inhibit policy mapping
            # or require that each certificate in a chain contain an acceptable
            # policy identifier. For more information about the use of this
            # extension see RFC 5280.
            # (https://cryptography.io/en/latest/x509/reference/#cryptography.x509.PrecertificateSignedCertificateTimestamps)

            return [
                (
                    name + "_REQUIRE_EXPLICIT_POLICY", extension.require_explicit_policy),
                (
                    name + "_INHIBIT_POLICY_MAPPING", extension.inhibit_policy_mapping
                )
            ]
        elif isinstance(extension, x509.FreshestCRL):
            # The freshest CRL extension (also known as Delta CRL Distribution
            # Point) identifies how delta CRL information is obtained. It is an
            # iterable, containing one or more DistributionPoint instances.
            # (https://cryptography.io/en/latest/x509/reference/#cryptography.x509.FreshestCRL)

            # existence might be interesting?
            return [(name, True)]
        elif isinstance(extension, x509.IssuingDistributionPoint):
            # Issuing distribution point is a CRL extension that identifies the
            # CRL distribution point and scope for a particular CRL. It
            # indicates whether the CRL covers revocation for end entity
            # certificates only, CA certificates only, attribute certificates
            # only, or a limited set of reason codes. For specific details on
            # the way this extension should be processed see RFC 5280.
            # (https://cryptography.io/en/latest/x509/reference/#cryptography.x509.IssuingDistributionPoint)

            # should only be present in CRL certs, hence not in ones retrieved from the CT logs
            # -> check
            return [(name, True)]
        elif name in ["POLICY_MAPPINGS", "SUBJECT_DIRECTORY_ATTRIBUTES"]:
            # not implemented in this library, i.e. x509.PolicyMappings does not exist
            return []

        return [(name, "unkown")]
    except x509.ExtensionNotFound:
        return []


def map_certificate_extensions(extensions: x509.Extensions) -> List[Tuple[str, Any]]:
    return [
        # flatten output of map_certificate_extension
        t
        for name in extension_object_identifier_names
        for t in map_certificate_extension(f"EXTENSION_{name}", extensions, getattr(x509.ExtensionOID, name))
    ]


def map_certificate_row(row):
    # parse PEM certificate format
    cert = x509.load_pem_x509_certificate(
        # decode ascii string to bytes
        (
            # add PEM prefix
            "-----BEGIN CERTIFICATE-----" +
            row['certificate_base64'] +
            # and PEM suffix
            "-----END CERTIFICATE-----"
        ).encode("ascii")
    )

    # cert.subject.get_attributes_for_oid(NameOID.COMMON_NAME)

    mapped_extensions = map_certificate_extensions(cert.extensions)
    extension_labels = [x[0] for x in mapped_extensions]
    extension_values = [x[1] for x in mapped_extensions]

    return pd.Series(
        [
            map_certificate_version(cert),
            map_certificate_datetime(cert.not_valid_before),
            map_certificate_datetime(cert.not_valid_after),
            map_certificate_datetime(
                cert.not_valid_after) - map_certificate_datetime(cert.not_valid_before),
        ] +
        map_certificate_name(cert.issuer) +
        map_certificate_name(cert.subject) +
        [
            cert.signature_hash_algorithm.name if cert.signature_hash_algorithm != None else None,
            map_certificate_signature_algorithm_oid(
                cert.signature_algorithm_oid
            )
        ] +
        extension_values,
        index=[
            'version',
            'not_valid_before',
            'not_valid_after',
            'validity_time',
        ] +
        ['issuer_' + name for name in names_object_identifier_names] +
        ['subject_' + name for name in names_object_identifier_names] +
        [
            'signature_hash_algorithm',
            'signature_algorithm'
        ] +
        extension_labels
    )
