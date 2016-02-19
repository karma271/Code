button_names = ["hazard","park","lane","track","AWD","Sport"]
required_filename=("1R Hazard INS 1").lower()



for i in range(len(button_names)):
    if button_names[i] in required_filename:
        required_button_name = button_names[i]
        print required_button_name
