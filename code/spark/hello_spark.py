from pyspark import SparkConf, SparkContext

def main():
    conf = SparkConf().setAppName("Hello Python Spark")
    sc = SparkContext(conf=conf)

    print("Spark version:            ", sc.version)
    print("Spark master:             ", sc.master)
    print("Spark running 'locally'?: ", sc.master.startswith("local"))

    sc.stop()

if __name__ == "__main__":
    main()
