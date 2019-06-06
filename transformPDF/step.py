from settings import USE_DB
from generator2postgre import MyPdfZip as DB_MyPDFZip
from generator2current import MyPdfZip as NODB_MyPDFZip

def main():
    if USE_DB == 'true':
        taster = DB_MyPDFZip()
        taster.run()
        taster.conn.close()
    if USE_DB == 'false':
        taster = NODB_MyPDFZip()
        taster.run()




if __name__ == "__main__":
    main()