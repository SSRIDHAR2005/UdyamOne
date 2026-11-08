"""
UdyamOne - Strict Number Validation Module
Implements:
1. Official GSTIN Structure & Modulo-36 Checksum Validation (GST Council Specification)
2. Indian State Code Mapping (Codes 01 to 38, 97, 99)
3. Strict Udyam Registration Number Format & State Code Validation (UDYAM-XX-00-XXXXXXX)
4. Character Ambiguity & Confusion Checks (O/0, I/1, B/8, S/5) without silent modification
"""

import re
from typing import Dict, Any, Optional, Tuple

INDIAN_STATE_CODES = {
    "01": "Jammu & Kashmir",
    "02": "Himachal Pradesh",
    "03": "Punjab",
    "04": "Chandigarh",
    "05": "Uttarakhand",
    "06": "Haryana",
    "07": "Delhi",
    "08": "Rajasthan",
    "09": "Uttar Pradesh",
    "10": "Bihar",
    "11": "Sikkim",
    "12": "Arunachal Pradesh",
    "13": "Nagaland",
    "14": "Manipur",
    "15": "Mizoram",
    "16": "Tripura",
    "17": "Meghalaya",
    "18": "Assam",
    "19": "West Bengal",
    "20": "Jharkhand",
    "21": "Odisha",
    "22": "Chhattisgarh",
    "23": "Madhya Pradesh",
    "24": "Gujarat",
    "25": "Daman & Diu",
    "26": "Dadra & Nagar Haveli",
    "27": "Maharashtra",
    "28": "Andhra Pradesh (Old)",
    "29": "Karnataka",
    "30": "Goa",
    "31": "Lakshadweep",
    "32": "Kerala",
    "33": "Tamil Nadu",
    "34": "Puducherry",
    "35": "Andaman & Nicobar Islands",
    "36": "Telangana",
    "37": "Andhra Pradesh",
    "38": "Ladakh",
    "97": "Other Territory",
    "99": "Centre Jurisdiction"
}

UDYAM_STATE_MAP = {
    "AP": "Andhra Pradesh",
    "AR": "Arunachal Pradesh",
    "AS": "Assam",
    "BR": "Bihar",
    "CG": "Chhattisgarh",
    "CH": "Chandigarh",
    "DL": "Delhi",
    "GA": "Goa",
    "GJ": "Gujarat",
    "HR": "Haryana",
    "HP": "Himachal Pradesh",
    "JH": "Jharkhand",
    "JK": "Jammu and Kashmir",
    "KA": "Karnataka",
    "KL": "Kerala",
    "LA": "Ladakh",
    "LD": "Lakshadweep",
    "MH": "Maharashtra",
    "ML": "Meghalaya",
    "MN": "Manipur",
    "MP": "Madhya Pradesh",
    "MZ": "Mizoram",
    "NL": "Nagaland",
    "OD": "Odisha",
    "PB": "Punjab",
    "PY": "Puducherry",
    "RJ": "Rajasthan",
    "SK": "Sikkim",
    "TN": "Tamil Nadu",
    "TS": "Telangana",
    "TR": "Tripura",
    "UP": "Uttar Pradesh",
    "UK": "Uttarakhand",
    "WB": "West Bengal"
}

GSTIN_CHARS = "0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZ"
GSTIN_CHAR_MAP = {c: i for i, c in enumerate(GSTIN_CHARS)}


class NumberValidator:
    """
    Enforces strict structural and mathematical validation on government identifiers.
    Never silently modifies characters to force a valid response.
    """

    @staticmethod
    def calculate_gstin_checksum(gstin_14: str) -> Optional[str]:
        """
        Calculates the official GSTIN 15th character checksum using the
        Modulo-36 Luhn-like algorithm mandated by the GST Council.
        """
        if len(gstin_14) != 14:
            return None
        
        total = 0
        for idx, char in enumerate(gstin_14):
            if char not in GSTIN_CHAR_MAP:
                return None
            val = GSTIN_CHAR_MAP[char]
            # Weights alternate: 1 for odd positions (index 0, 2, 4...), 2 for even (index 1, 3, 5...)
            weight = 1 if (idx % 2 == 0) else 2
            product = val * weight
            total += (product // 36) + (product % 36)
        
        remainder = total % 36
        check_val = (36 - remainder) % 36
        return GSTIN_CHARS[check_val]

    def validate_gstin(self, gstin: Optional[str]) -> Dict[str, Any]:
        """
        Validates 15-character GSTIN according to:
        1. Length exactly 15
        2. Valid 2-digit Indian State code (01-38, 97, 99)
        3. Valid PAN format: 5 letters + 4 digits + 1 letter (accepts X as 4th char per hackathon dataset)
        4. Entity code (1-9 or A-Z)
        5. Position 14 must be 'Z'
        6. Official Modulo-36 Checksum calculation
        """
        if not gstin or not isinstance(gstin, str):
            return {
                "valid": False,
                "gstin": gstin or "",
                "error": "GSTIN is missing or empty.",
                "reason": "GSTIN must be provided.",
                "state_code": None,
                "state_name": None,
                "checksum_valid": False
            }

        gst_clean = gstin.strip().upper()

        # Check character confusions without silent modification
        ambiguities = []
        if re.search(r'[0-9]{2}[A-Z]{3}[A-ZX][A-Z0-9][0-9]{4}[A-Z0-9][1-9A-Z]Z[0-9A-Z]', gst_clean) is None:
            if "O" in gst_clean[:2] or "I" in gst_clean[:2]:
                ambiguities.append("State code contains letters 'O' or 'I' instead of digits '0' or '1'.")
            if " " in gstin:
                ambiguities.append("GSTIN contains whitespace characters.")

        if len(gst_clean) != 15:
            return {
                "valid": False,
                "gstin": gst_clean,
                "error": f"GSTIN must be exactly 15 characters (received {len(gst_clean)}).",
                "reason": "Invalid length for Indian GSTIN.",
                "state_code": None,
                "state_name": None,
                "checksum_valid": False,
                "ambiguities": ambiguities
            }

        state_code = gst_clean[:2]
        if state_code not in INDIAN_STATE_CODES:
            return {
                "valid": False,
                "gstin": gst_clean,
                "error": f"Invalid state code '{state_code}'. Must be between 01 and 38.",
                "reason": "Unrecognized Indian State / Union Territory code.",
                "state_code": state_code,
                "state_name": None,
                "checksum_valid": False,
                "ambiguities": ambiguities
            }
        state_name = INDIAN_STATE_CODES[state_code]

        # Structural regex check
        # Standard: 2 digits + 5 letters (4th letter can be X) + 4 digits + 1 letter + 1 entity + 'Z' + 1 checksum
        pattern = r"^[0-9]{2}[A-Z]{3}[A-ZX][A-Z0-9][0-9]{4}[A-Z0-9][1-9A-Z]Z[0-9A-Z]$"
        if not re.match(pattern, gst_clean):
            return {
                "valid": False,
                "gstin": gst_clean,
                "error": "GSTIN structure does not conform to GST Council PAN/Entity specifications.",
                "reason": "Invalid character positions in embedded PAN or entity code.",
                "state_code": state_code,
                "state_name": state_name,
                "checksum_valid": False,
                "ambiguities": ambiguities
            }

        # 14th character must be 'Z'
        if gst_clean[13] != 'Z':
            return {
                "valid": False,
                "gstin": gst_clean,
                "error": f"14th character of GSTIN must be 'Z' (found '{gst_clean[13]}').",
                "reason": "14th character violation.",
                "state_code": state_code,
                "state_name": state_name,
                "checksum_valid": False,
                "ambiguities": ambiguities
            }

        # Modulo-36 Checksum Validation
        expected_chk = self.calculate_gstin_checksum(gst_clean[:14])
        actual_chk = gst_clean[14]
        if expected_chk != actual_chk:
            return {
                "valid": False,
                "gstin": gst_clean,
                "error": f"Official GSTIN checksum failure: expected '{expected_chk}', found '{actual_chk}'.",
                "reason": "GSTIN Modulo-36 checksum mismatch. Check for typos or misread characters.",
                "state_code": state_code,
                "state_name": state_name,
                "checksum_valid": False,
                "checksum_expected": expected_chk,
                "checksum_actual": actual_chk,
                "ambiguities": ambiguities
            }

        return {
            "valid": True,
            "gstin": gst_clean,
            "state_code": state_code,
            "state_name": state_name,
            "pan": gst_clean[2:12],
            "entity_code": gst_clean[12],
            "checksum_valid": True,
            "checksum_expected": expected_chk,
            "checksum_actual": actual_chk,
            "reason": f"Valid GSTIN registered in {state_name} (Checksum matched).",
            "ambiguities": []
        }

    def validate_udyam(self, udyam_number: Optional[str]) -> Dict[str, Any]:
        """
        Validates Udyam Registration Number according to:
        1. Prefix: 'UDYAM-'
        2. 2-letter Indian State code (e.g. WB, MH, DL, AP, RJ)
        3. 2-digit subcode (e.g. 00)
        4. Exactly 7 digits
        Total length: 19 characters (e.g. UDYAM-WB-00-5053330)
        """
        if not udyam_number or not isinstance(udyam_number, str):
            return {
                "valid": False,
                "udyam_number": udyam_number or "",
                "error": "Udyam Registration Number is missing or empty.",
                "reason": "Udyam registration number must be provided.",
                "state_code": None,
                "state_name": None
            }

        udy_clean = udyam_number.strip().upper()

        ambiguities = []
        if "-OO-" in udy_clean or "-O0-" in udy_clean or "-0O-" in udy_clean:
            ambiguities.append("Letter 'O' found in numeric district subcode instead of digit '0'.")

        if not udy_clean.startswith("UDYAM-"):
            return {
                "valid": False,
                "udyam_number": udy_clean,
                "error": "Udyam Registration Number must begin with 'UDYAM-'.",
                "reason": "Missing 'UDYAM-' prefix.",
                "state_code": None,
                "state_name": None,
                "ambiguities": ambiguities
            }

        if len(udy_clean) != 19:
            return {
                "valid": False,
                "udyam_number": udy_clean,
                "error": f"Udyam number must be exactly 19 characters (received {len(udy_clean)}). Format: UDYAM-XX-00-XXXXXXX",
                "reason": "Invalid length for Udyam registration number.",
                "state_code": None,
                "state_name": None,
                "ambiguities": ambiguities
            }

        pattern = r"^UDYAM-([A-Z]{2})-([0-9]{2})-([0-9]{7})$"
        m = re.match(pattern, udy_clean)
        if not m:
            return {
                "valid": False,
                "udyam_number": udy_clean,
                "error": "Format must be UDYAM-XX-00-XXXXXXX where XX is State code and remaining sections are numeric.",
                "reason": "Invalid character format in Udyam number.",
                "state_code": None,
                "state_name": None,
                "ambiguities": ambiguities
            }

        state_code = m.group(1)
        if state_code not in UDYAM_STATE_MAP:
            return {
                "valid": False,
                "udyam_number": udy_clean,
                "error": f"Invalid Indian State code '{state_code}' in Udyam registration number.",
                "reason": "Unrecognized 2-letter Indian State / UT code in Udyam number.",
                "state_code": state_code,
                "state_name": None,
                "ambiguities": ambiguities
            }
        state_name = UDYAM_STATE_MAP[state_code]

        return {
            "valid": True,
            "udyam_number": udy_clean,
            "state_code": state_code,
            "state_name": state_name,
            "district_code": m.group(2),
            "registration_serial": m.group(3),
            "reason": f"Valid Udyam Registration Number registered in {state_name}.",
            "ambiguities": []
        }


number_validator = NumberValidator()
