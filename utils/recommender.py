from sklearn.model_selection import train_test_split
from rec_sys_app.models import Transaction
import turicreate as tc
import pandas as pd


class Recommender:
    def __init__(self):
        self. model = ""

    # def clean(self, input_path, output_path):
    #     """
    #     clean dirty static when necessary abd return clean transaction.
    #     :param input_path:
    #     :param output_path:
    #     :return: pandas-DataFrame
    #     """
    #     transactions = pd.read_csv(input_path)
    #     df_out = pd.DataFrame(columns=["customerID", "products"])
    #
    #     count = 0
    #     for id, row in transactions.iterrows():
    #         u_id = row["customerID"]
    #         trans = row["products"]
    #         trans = trans.split("|")
    #         trans = list(map(int, trans))
    #         for p_id in trans:
    #             df_out.at[count, "customerID"] = u_id
    #             df_out.at[count, "products"] = p_id
    #             count += 1
    #     df_out.to_csv(output_path, encoding='utf-8')
    #     return df_out

    def pull_transactions(self):
        df_out = pd.DataFrame(columns=["customerID", "productID"])
        transactions = Transaction.objects.all()
        customerID = []
        productID = []
        for t in transactions:
            # print(type(t.uid))  # string
            customerID.append(t.uid)
            productID.append(t.pid)
        df_out["customerID"] = customerID
        df_out["productID"] = productID
        return df_out

    def normalize_transaction_data(self, transactions, method=0):
        """
        convert transaction data into reduced counting table.[customerID, productID, Purchase_Count]
        :param transactions: pandas-DataFrame, columns=["customerID", "productID"]
        :param method: 0: raw count; 1: dummy_count; 2: Normalize item values across users
        :return: pandas-DataFrame, columns=["customerID", "productID", "Purchase_Count"]
        """
        if method == 0:
            data = pd.melt(transactions, id_vars=['customerID'], value_name='products') \
                .dropna().drop(['variable'], axis=1) \
                .groupby(['customerID', 'products']) \
                .agg({'products': 'count'}) \
                .rename(columns={'products': 'Purchase_Count'}) \
                .reset_index() \
                .rename(columns={'products': 'productID'})
        elif method == 1:
            data = []
        else:
            data = []
        return data

    def split_data(self, data, r=0.2):
        """
        :param data: pandas.DataFrame
        :param r: splitting ratio
        :return: train_data (tc.SFrame)
                 test_data (tc.SFrame)
        """
        train, test = train_test_split(data, test_size=r)
        train_data = tc.SFrame(train)
        test_data = tc.SFrame(test)
        return train_data, test_data

    def train_model(self, train_data, name, user_id, item_id, target):
        if name == 'popularity':
            model = tc.popularity_recommender.create(train_data,
                                                     user_id=user_id,
                                                     item_id=item_id,
                                                     target=target)
        elif name == 'cosine':
            model = tc.item_similarity_recommender.create(train_data,
                                                          user_id=user_id,
                                                          item_id=item_id,
                                                          target=target,
                                                          similarity_type='cosine')
        elif name == 'pearson':
            model = tc.item_similarity_recommender.create(train_data,
                                                          user_id=user_id,
                                                          item_id=item_id,
                                                          target=target,
                                                          similarity_type='pearson')
        self.model = model
        return self.model


def main():
    input_path = "../static/recommend_1.csv"
    output_path = "../static/transaction.csv"

    user_id = 'customerID'
    item_id = 'productID'
    users_to_recommend = [0]
    n_rec = 10  # number of items to recommend
    n_display = 30  # to display the first few rows in an output dataset
    name = 'cosine'
    target = 'Purchase_Count'

    # create recommender
    recommender = Recommender()

    # pull up transactions form DB
    transactions = recommender.pull_transactions()

    data = recommender.normalize_transaction_data(transactions, method=0)
    train_data, test_data = recommender.split_data(data, r=.2)

    # train
    model = recommender.train_model(train_data, name, user_id, item_id, target, users_to_recommend, n_rec, n_display)

    # query
    recom = model.recommend(users=users_to_recommend, k=n_rec)
    recom = pd.DataFrame(recom)
    print(recom)
    recom = recom["productID"]
    return list(recom)


if __name__ == '__main__':
    main()
