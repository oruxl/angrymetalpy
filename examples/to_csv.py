import angrymetalpy as amp

if __name__ == '__main__':
    print("Reading from JSON, writing to CSV")
    reviews = amp.reviews_from_json('data_20180422.txt')
    for r in reviews:
        print(r)
        with open('tst.csv', 'a') as f:
            f.write(r.csv().encode('utf8') + "\n")

    print("Reading from CSV")
    reviews = amp.reviews_from_csv('tst.csv')
    for r in reviews[:10]:
        print(r)
