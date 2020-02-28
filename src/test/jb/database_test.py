from ...jb.database import Session, FPHistoryData


with Session() as session:
    r: FPHistoryData = session.query(
        FPHistoryData).filter_by(idcard='430311197209271512').first()
    print(r)
    if r:
        print(r.name)
