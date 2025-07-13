from database.mongo import HMI_CLASS_REG


def delete_All():
 HMI_CLASS_REG.delete_many({})
