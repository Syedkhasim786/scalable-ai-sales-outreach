def build_prompt(name, role, company, industry, product, tone):

    return f"""
    Write a highly personalized sales outreach message.

    Lead Details:
    Name: {name}
    Role: {role}
    Company: {company}
    Industry: {industry}

    Product:
    {product}

    Tone:
    {tone}

    Requirements:
    - Make it very personalized
    - Mention role and company context
    - Keep it short and engaging
    - Add strong hook + CTA

    Output format (STRICT JSON):
    {{
      "subject": "...",
      "email": "...",
      "linkedin": "...",
      "whatsapp": "..."
    }}
    """
