import manga109api

bb_categories = ["frame", "text", "face", "body"]


def bb_iter(title, manga109_root_dir, categories=bb_categories):
    for i_page, page in enumerate(
            Book(title, manga109_root_dir).get_page_iter()):
        for i_category, bbtype in enumerate(categories):
            for bb in page.get_bbs()[bbtype]:
                yield i_page, i_category, bb


class Page(object):
    def __init__(self, book, page_index):
        self.book = book
        self.page_index = page_index

        self.width = self.book.annotations["page"][self.page_index]["@width"]
        self.height = self.book.annotations["page"][self.page_index]["@height"]

    def get_bbs(self):
        bb_dict = dict([(a,[d for d in self.book.annotations["page"][self.page_index][a]]) for a in bb_categories])
        return bb_dict


class Book(object):
    def __init__(self, book, manga109_root_dir):
        self.book = book
        self.parser = manga109api.Parser(manga109_root_dir)
        self.annotations = self.parser.get_annotation(book=book)
        self.n_pages = len(self.annotations["page"])

    def get_page_iter(self):
        for page_index in range(self.n_pages):
            yield Page(self, page_index)
