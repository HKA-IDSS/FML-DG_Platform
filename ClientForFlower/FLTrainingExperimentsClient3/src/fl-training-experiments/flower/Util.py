from sklearn.datasets import load_wine


def read_data(dataset: str):
    if dataset == "wine":
        X, y = load_wine(return_X_y=True)
    elif dataset == "adult":
        X = None
        y= None
        print("To be developed")
    return X, y