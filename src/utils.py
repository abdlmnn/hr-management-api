def email_notification_body(email_body: str):
    texts = """<body style="background-color: #e9ecef;">
            <table border="0" cellpadding="0" cellspacing="0" width="100%">
                <tr>
                    <td align="center" bgcolor="#e9ecef">
                    <table border="0" cellpadding="0" cellspacing="0" width="100%" style="max-width: 600px;">
                        <tr>
                            <td bgcolor="#ffffff" align="center" valign="top" style="padding: 0px 24px 0; border-top: 3px solid #d4dadf;"> 
                                <a href="https://www.iliganlight.com" target="_blank" style="display: inline-block;">
                                <img src="https://iliganlight.com/assets/images/ilpi_email_header.png" alt="ILIGAN LIGHT & POWER, INC." border="0" width="500" style="display: block; width: 500px; max-width: 500px; min-width: 48px;">
                                </a>
                            </td>
                        </tr>
                    </table>
                    </td>
                </tr>
                <tr>
                    <td align="center" bgcolor="#e9ecef">
                    <table border="0" cellpadding="0" cellspacing="0" width="100%" style="max-width: 600px;">
                        <tr>
                            <td align="left" bgcolor="#ffffff" style="padding: 36px 24px 0; font-family: 'Source Sans Pro', Helvetica, Arial, sans-serif; border-top: 3px solid #d4dadf;">
                                <p style="margin: 0; font-size: 14px;">
                                email_body
                                </p>
                            </td>
                        </tr>
                    </table>
                    </td>
                </tr>
            </table>
        </body>"""
    texts = texts.replace("email_body", email_body)
    return texts
