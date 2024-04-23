from Tools import BookInfo

book_retriever = BookInfo.db.as_retriever(
    search_type="similarity_score_threshold", search_kwargs={"score_threshold": 0.5, "k": 4}
)

res = book_retriever.get_relevant_documents("tôi muốn tìm sách của Hồ Văn Đằng")

print(res)