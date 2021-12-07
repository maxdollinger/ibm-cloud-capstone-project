// https://2e35c4b8.eu-gb.apigw.appdomain.cloud/api/review

const Cloudant = require('@cloudant/cloudant');

async function main(params) {

    const cloudant = Cloudant({
        url: params.URL,
        plugins: { iamauth: { iamApiKey: params.API_KEY } }
    });

    const db = cloudant.db.use('reviews');

    try {
        if (params.__ow_method === "get") {
            const selector = {
                "dealership": {
                    "$eq": Number(params.dealerId)
                }
            };

            const docs = await (new Promise((res, rej) => {
                db.find({ selector }, function (err, result) {
                    if (err) rej(err);

                    res(result.docs)
                });
            }));

            return { body: docs}
        } else if (params.__ow_method === "post") {
            const response = await db.insert(params.review);

            return { body: response };
        } else {
            throw Error("Only GET or POST allowed")
        }
    } catch (error) {
        return { error: error.description };
    }
}