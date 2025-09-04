import datetime

class Client:
    def __init__(
            self,
            group: str = None,
            client_type: str = None,
            client_name: str = None,
            client_address: str = None,
            client_email: str = None,
            client_phone: str = None,
            disburse_date: datetime.date = None,
    ):
        self.group = group
        self.client_type = client_type
        self.client_name = client_name
        self.client_address = client_address
        self.client_email = client_email
        self.client_phone = client_phone
        self.disburse_date = disburse_date

    def to_dict(self):
        return {
            "group": self.group,
            "client_type": self.client_type,
            "client_name": self.client_name,
            "client_address": self.client_address,
            "client_email": self.client_email,
            "client_phone": self.client_phone,
            "disburse_date": self.disburse_date,
        }



class GroupClient(Client):
    def __init__(
            self,
            NTN: str,
            group: str = "Group",
            client_type: str = None,
            client_name: str = None,
            client_address: str = None,
            client_email: str = None,
            client_phone: str = None,
            disburse_date: datetime.date = None,
    ):
        super().__init__(
            group=group,
            client_type=client_type,
            client_name=client_name,
            client_address=client_address,
            client_email=client_email,
            client_phone=client_phone,
            disburse_date=disburse_date
        )
        self.NTN = NTN

    def to_dict(self):
        return {**super().to_dict(), "NTN": self.NTN}


class IndividualClient(Client):
    def __init__(
            self,
            CNIC: str,
            group: str = "Group",
            client_type: str = None,
            client_name: str = None,
            client_address: str = None,
            client_email: str = None,
            client_phone: str = None,
            disburse_date: datetime.date = None,
    ):
        super().__init__(
            group=group,
            client_type=client_type,
            client_name=client_name,
            client_address=client_address,
            client_email=client_email,
            client_phone=client_phone,
            disburse_date=disburse_date
        )
        self.CNIC = CNIC

    def to_dict(self):
        return {**super().to_dict(), "CNIC": self.CNIC}




### TODO


