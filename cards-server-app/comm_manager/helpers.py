def carousel(items):
    return {"type": "carousel", "contents": items}


def flex_json_card_image_with_price(image, price, url):
    return {
        "type": "bubble",
        "body": {
            "type": "box",
            "layout": "vertical",
            "contents": [
                {
                    "type": "image",
                    "url": image,
                    "size": "full",
                    "aspectMode": "cover",
                    "aspectRatio": "7:10",
                    "gravity": "center",
                },
                {
                    "type": "box",
                    "layout": "vertical",
                    "contents": [],
                    "position": "absolute",
                    "background": {
                        "type": "linearGradient",
                        "angle": "0deg",
                        "endColor": "#00000000",
                        "startColor": "#00000099",
                    },
                    "width": "100%",
                    "height": "40%",
                    "offsetBottom": "0px",
                    "offsetStart": "0px",
                    "offsetEnd": "0px",
                },
                {
                    "type": "box",
                    "layout": "horizontal",
                    "contents": [
                        {
                            "type": "box",
                            "layout": "vertical",
                            "contents": [
                                {
                                    "type": "box",
                                    "layout": "horizontal",
                                    "contents": [
                                        {
                                            "type": "text",
                                            "text": "CKD 🔗",
                                            "size": "lg",
                                            "color": "#ffffff",
                                            "align": "end",
                                        }
                                    ],
                                },
                                {
                                    "type": "box",
                                    "layout": "horizontal",
                                    "contents": [
                                        {
                                            "type": "text",
                                            "text": f"${price}",
                                            "color": "#ffffff",
                                            "size": "md",
                                            "align": "end",
                                        }
                                    ],
                                },
                            ],
                            "spacing": "xs",
                        }
                    ],
                    "position": "absolute",
                    "offsetBottom": "50%",
                    "offsetStart": "50%",
                    "offsetEnd": "0px",
                    "paddingAll": "15px",
                    "paddingEnd": "22px",
                    "background": {
                        "type": "linearGradient",
                        "startColor": "#99999900",
                        "endColor": "#999999AA",
                        "centerColor": "#99999955",
                        "angle": "90deg",
                    },
                    "width": "50%",
                },
            ],
            "paddingAll": "0px",
        },
    }
