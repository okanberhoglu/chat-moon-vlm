    # parser = argparse.ArgumentParser()
    # parser.add_argument("--image_path", type=str, required=True, help="Path to the image file")
    # args = parser.parse_args()
    # model_name = "vikhyatk/moondream2"
    # try:
    #     model = AutoModelForCausalLM.from_pretrained(
    #         model_name, 
    #         revision="2025-06-21",
    #         trust_remote_code=True, 
    #         device_map="cpu"
    #     )

    # except OSError as e:
    #     print(f"Error loading model: {e}")
    #     return

    # image = Image.open(args.image_path)
    # enc_image = model.encode_image(image)

    # print("Ask questions about your image.")
    # while True:
    #     try:
    #         question = input("Question: ")
    #         answer = model.query(enc_image, question)['answer']
    #         print(f"Answer: {answer}\n")
            
    #     except KeyboardInterrupt:
    #         print("\nExiting.")
    #         break

    #     except Exception as e:
    #         print(f"Error: {e}")
    #         break